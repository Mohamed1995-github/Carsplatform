from rest_framework import serializers
from .models import Car, Listing, RentalTerms, CarImage, Availability
from agencies.serializers import AgencySerializer


class CarImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarImage
        fields = ['id', 'image', 'image_url', 'is_cover', 'sort_order', 'alt_text', 'created_at']
        read_only_fields = ['created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'date', 'is_available', 'reason']


class RentalTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalTerms
        fields = [
            'id', 'daily_rate', 'weekly_rate', 'monthly_rate', 'deposit_required',
            'min_rental_days', 'max_rental_days', 'pickup_location', 'return_location',
            'fuel_policy', 'mileage_limit'
        ]


class CarSerializer(serializers.ModelSerializer):
    agency = AgencySerializer(read_only=True)
    images = CarImageSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    availability = AvailabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Car
        fields = [
            'id', 'agency', 'make', 'model', 'year', 'mileage', 'fuel', 'transmission', 
            'body', 'engine_size', 'power', 'color', 'features', 'description', 'images', 
            'cover_image', 'availability', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_cover_image(self, obj):
        cover = obj.cover_image
        if cover:
            return CarImageSerializer(cover, context=self.context).data
        return None


class ListingSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    rental_terms = RentalTermsSerializer(read_only=True)
    current_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'car', 'type', 'status', 'price_sale', 'price_rent_daily',
            'price_rent_weekly', 'price_rent_monthly', 'is_featured', 'seo_title',
            'seo_description', 'rental_terms', 'current_price', 'created_at',
            'updated_at', 'published_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'published_at']
    
    def get_current_price(self, obj):
        return obj.current_price


class ListingSearchSerializer(serializers.Serializer):
    make = serializers.CharField(required=False)
    model = serializers.CharField(required=False)
    year_min = serializers.IntegerField(required=False, min_value=1900, max_value=2030)
    year_max = serializers.IntegerField(required=False, min_value=1900, max_value=2030)
    price_min = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    price_max = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    mileage_max = serializers.IntegerField(required=False, min_value=0)
    fuel = serializers.ChoiceField(choices=Car.FUEL_CHOICES, required=False)
    transmission = serializers.ChoiceField(choices=Car.TRANSMISSION_CHOICES, required=False)
    city = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=Listing.TYPE_CHOICES, required=False)
    
    def validate(self, data):
        if 'year_min' in data and 'year_max' in data:
            if data['year_min'] > data['year_max']:
                raise serializers.ValidationError("L'année minimum ne peut pas être supérieure à l'année maximum.")
        
        if 'price_min' in data and 'price_max' in data:
            if data['price_min'] > data['price_max']:
                raise serializers.ValidationError("Le prix minimum ne peut pas être supérieur au prix maximum.")
        
        return data


class CarCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
    )
    
    class Meta:
        model = Car
        fields = [
            'agency', 'make', 'model', 'year', 'mileage', 'fuel', 'transmission', 
            'body', 'engine_size', 'power', 'color', 'features', 'description', 'images'
        ]
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        car = Car.objects.create(**validated_data)
        
        for i, image_data in enumerate(images_data):
            CarImage.objects.create(
                car=car,
                image=image_data,
                sort_order=i,
                is_cover=(i == 0)  # First image is cover
            )
        
        return car


class ListingCreateSerializer(serializers.ModelSerializer):
    rental_terms = RentalTermsSerializer(required=False)
    
    class Meta:
        model = Listing
        fields = [
            'car', 'type', 'status', 'price_sale', 'price_rent_daily',
            'price_rent_weekly', 'price_rent_monthly', 'is_featured', 'seo_title',
            'seo_description', 'rental_terms'
        ]
    
    def create(self, validated_data):
        rental_terms_data = validated_data.pop('rental_terms', None)
        listing = Listing.objects.create(**validated_data)
        
        if rental_terms_data and listing.type == 'rent':
            RentalTerms.objects.create(listing=listing, **rental_terms_data)
        
        return listing

