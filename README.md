# Plateforme Voitures - Car Platform

Une plateforme complète de gestion de voitures pour les agences automobiles avec support multilingue (Français/Arabe).

## 🚀 Fonctionnalités

### Rôles et Permissions
- **Admin** : Gestion de la plateforme, modération des agences et annonces
- **Agence** : Propriétaire et staff pour gérer leurs voitures et réservations
- **Client** : Consultation et réservation (compte optionnel)

### Onboarding Agence
- Inscription avec vérification (K-bis/RC, téléphone, WhatsApp)
- Statuts : pending/approved/rejected/suspended
- Vérification des documents

### Catalogue de Voitures
- Création et édition de voitures avec photos multiples
- Options et caractéristiques détaillées
- Types d'annonces : vente ou location
- Gestion des disponibilités

### Recherche et Filtres
- Marque, modèle, année, prix, kilométrage
- Carburant, boîte de vitesse, ville
- Disponibilité pour location (dates)
- Recherche avancée avec multiples critères

### Contact et Communication
- Boutons WhatsApp, appel, message
- Formulaire de contact avec notifications
- Notifications email/WhatsApp automatiques

### Réservations
- Demande de réservation (location)
- RDV/essai (vente)
- Pas de paiement en ligne (paiement en agence uniquement)

### Back-office Agence
- Gestion des annonces
- Suivi des réservations
- Messages et demandes
- Statistiques simples

### Modération Admin
- Validation des agences et annonces
- Gestion des signalements
- Outils de modération

### Multilingue
- Support Français/Arabe
- Interface traduite
- Contenu multilingue

### SEO
- Balisage schema.org/Vehicle
- Pages marque/modèle/ville
- Optimisation pour les moteurs de recherche

### Conformité
- RGPD
- Consentement cookies
- CGU
- Mentions "paiement en agence uniquement"

## 🛠 Installation

### Prérequis
- Python 3.8+
- pip
- Git

### Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd carsplatforms
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**
```bash
# Copier le fichier d'environnement
cp .env.example .env
# Éditer les variables d'environnement
```

5. **Migrations de base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur**
```bash
python manage.py runserver
```

## 📁 Structure du Projet

```
carsplatforms/
├── agencies/          # Gestion des agences
├── cars/             # Gestion des voitures et annonces
├── bookings/         # Gestion des réservations
├── inquiries/        # Gestion des demandes de renseignements
├── carsplatform/     # Configuration principale
├── static/           # Fichiers statiques
├── templates/        # Templates HTML
├── media/           # Fichiers uploadés
└── locale/          # Fichiers de traduction
```

## 🔌 API Endpoints

### Agences
- `GET /api/agencies/` - Liste des agences approuvées
- `GET /api/agencies/{id}/` - Détails d'une agence
- `POST /api/agencies/register/` - Inscription d'une agence
- `PUT /api/agencies/{id}/verify/` - Vérifier une agence (admin)

### Voitures
- `GET /api/cars/` - Liste des voitures
- `GET /api/cars/{id}/` - Détails d'une voiture
- `GET /api/cars/{id}/images/` - Images d'une voiture
- `GET /api/cars/{id}/availability/` - Disponibilité d'une voiture

### Annonces
- `GET /api/listings/` - Liste des annonces publiées
- `GET /api/listings/{id}/` - Détails d'une annonce
- `GET /api/listings/search/` - Recherche avancée
- `GET /api/listings/featured/` - Annonces en vedette

### Réservations
- `GET /api/bookings/` - Liste des réservations (admin)
- `POST /api/bookings/create/` - Créer une réservation
- `PUT /api/bookings/{id}/confirm/` - Confirmer une réservation
- `PUT /api/bookings/{id}/cancel/` - Annuler une réservation

### Demandes de Renseignements
- `GET /api/inquiries/` - Liste des demandes (admin)
- `POST /api/inquiries/create/` - Créer une demande
- `POST /api/inquiries/{id}/reply/` - Répondre à une demande
- `POST /api/contact/` - Formulaire de contact

## 🗄 Modèles de Données

### Agences
- `Agency` : Informations de l'agence
- `AgencyUser` : Utilisateurs liés à l'agence

### Voitures
- `Car` : Informations de la voiture
- `Listing` : Annonces (vente/location)
- `RentalTerms` : Conditions de location
- `CarImage` : Images des voitures
- `Availability` : Disponibilité des voitures

### Réservations
- `Booking` : Réservations et essais
- `BookingNotification` : Notifications de réservation

### Demandes
- `Inquiry` : Demandes de renseignements
- `InquiryResponse` : Réponses aux demandes

## 🌐 Multilingue

Le projet supporte le français et l'arabe :

1. **Traductions d'interface** : Fichiers dans `locale/`
2. **Contenu multilingue** : Champs avec suffixe `_ar`
3. **Configuration** : `LANGUAGES` dans `settings.py`

## 🔧 Configuration

### Variables d'environnement (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Base de données
- SQLite par défaut (développement)
- PostgreSQL recommandé pour la production

### Email
- Console backend pour le développement
- SMTP configuré pour la production

## 🚀 Déploiement

### Production
1. Configurer les variables d'environnement
2. Utiliser PostgreSQL
3. Configurer un serveur SMTP
4. Configurer un serveur web (nginx + gunicorn)
5. Configurer les fichiers statiques

### Docker (optionnel)
```bash
docker-compose up -d
```

## 📝 Tests

```bash
python manage.py test
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 📞 Support

Pour toute question ou support, contactez l'équipe de développement.

---

**Note** : Ce projet est un MVP (Minimum Viable Product) et peut être étendu selon les besoins spécifiques.

