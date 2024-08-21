# Gestion des Extincteurs - CRTV

## Description

Ce projet est une application Django pour la gestion des extincteurs au sein d'une entreprise comme la CRTV. Elle permet de créer, modifier, et supprimer des extincteurs, d'effectuer des inspections périodiques (manuelles, trimestrielles, semestrielles, et annuelles), et de générer des rapports d'inspection. L'application gère différents types d'utilisateurs avec des rôles spécifiques.

## Fonctionnalités

- **Gestion des extincteurs** : Créer, modifier, et supprimer des extincteurs.
- **Inspection des extincteurs** :
  - **Inspection manuelle** : Effectuée par les personnels de sécurité.
  - **Inspection trimestrielle** : Effectuée par les personnels de sécurité.
  - **Inspection semestrielle** : Effectuée par les personnels de sécurité.
  - **Inspection annuelle** : Effectuée par un expert professionnel externe.
- **Maintenance des extincteurs** : Programmée lors des inspections annuelles ou à tout moment en cas de besoin.
- **Notification par email** : Les utilisateurs sont notifiés 1 jour avant la date d'une inspection programmée.
- **Rapport d'inspection de sécurité (RIS)** : Génération de rapports en PDF après chaque inspection, comprenant une check-list et des commentaires.
- **Dashboard** : Visualisation des statistiques des inspections et des extincteurs.

## Modèles de données

### Utilisateur
- `Super utilisateur` : Directeur de service de sécurité, seul administrateur.
- `Personnel de sécurité` : Responsable des inspections manuelles, trimestrielles, et semestrielles.
- `Expert professionnel externe` : Responsable de l'inspection annuelle et de la maintenance.

### Extincteur
- `Type` : Eau, Mousse, Poudre, CO2.
- `Classe de feu` : Classe A, B, C, D, F (selon le type d'extincteur).
- `Date d'achat` : Date de mise en service de l'extincteur.
- `Localisation` : Emplacement de l'extincteur dans l'entreprise.

### Inspection
- `Date` : Date de l'inspection.
- `Type` : Manuelle, Trimestrielle, Semestrielle, Annuelle.
- `Inspecteur` : Utilisateur ayant réalisé l'inspection.
- `Commentaires` : Observations supplémentaires.

### Maintenance
- `Date` : Date de la maintenance.
- `Type` : Maintenance programmée ou immédiate.
- `Expert` : Expert professionnel ayant réalisé la maintenance.

### Notification
- `Date de notification` : Date d'envoi de la notification.
- `Destinataire` : Utilisateur recevant la notification.
- `Message` : Contenu du message de notification.

### Rapport d'inspection de sécurité (RIS)
- `Date` : Date du rapport.
- `Inspecteur` : Utilisateur ayant réalisé l'inspection.
- `Check-list` : Liste de vérifications effectuées sur les extincteurs inspectés.
- `Commentaires` : Résumé des observations.
- `PDF` : Rapport généré en PDF.

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-repo/gestion-extincteurs.git

2. Accédez au répertoire du projet :
   ```bash
    cd gestion-extincteurs

3. Créez un environnement virtuel :
    ```bash
    python -m venv env

4. Activez l'environnement virtuel :
    ```bash
    source env/bin/activate

5. Installez les dépendances :
    ```bash
    pip install -r requirements.txt

6. Appliquez les migrations :
    ```bash
    python manage.py migrate

7. Créez un super utilisateur :
    ```bash
    python manage.py createsuperuser

8. Lancez le serveur de développement :
    ```bash
    python manage.py runserver

## Utilisation

Connectez-vous en tant que super utilisateur pour gérer les extincteurs, les inspections, et les utilisateurs.
Les personnels de sécurité peuvent se connecter pour réaliser les inspections manuelles, trimestrielles, et semestrielles.
L'expert professionnel externe peut se connecter pour réaliser l'inspection annuelle et la maintenance des extincteurs.

## Dashboard

### Le tableau de bord permet de visualiser :

- La courbe de respect des inspections.
- Le nombre total d'inspections réalisées.
- Les statistiques sur les types d'extincteurs.

## Contribution

Les contributions sont les bienvenues ! Veuillez créer une pull request pour toute suggestion ou modification.

## Licence

Ce projet est sous licence privee