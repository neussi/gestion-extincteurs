from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
from django.db import models
from datetime import timedelta
from django.utils import timezone

class Utilisateur(models.Model):
    TYPE_CHOICES = [
        ('personnel', 'Personnel'),
        ('expert', 'Expert'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    tel = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    poste = models.CharField(max_length=100)
    type_utilisateur = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f'{self.nom} {self.prenom} ({self.poste} - {self.type_utilisateur})'



def generate_extincteur_code():
    return f'E{uuid.uuid4().hex[:4]}'

class Extincteur(models.Model):
    TYPE_CHOICES = [
        ('eau', 'Eau'),
        ('mousse', 'Mousse'),
        ('poudre', 'Poudre'),
        ('co2', 'CO2'),
    ]
    
    CLASSE_CHOICES = [
        ('A', 'Classe A'),
        ('B', 'Classe B'),
        ('C', 'Classe C'),
        ('D', 'Classe D'),
        ('F', 'Classe F'),
    ]
    
    code = models.CharField(max_length=5, primary_key=True, default=generate_extincteur_code, editable=False)
    type_extincteur = models.CharField(max_length=10, choices=TYPE_CHOICES)
    classe = models.CharField(max_length=2, choices=CLASSE_CHOICES, default="A")
    date_achat = models.DateField()
    date_valid = models.DateField(default=date(2024, 8, 24))
    localisation = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.code} - {self.type_extincteur} ({self.localisation})'


class Inspection(models.Model):
    TYPE_INSPECTION_CHOICES = [
        ('manuelle', 'Manuelle'),
        ('trimestrielle', 'Trimestrielle'),
        ('semestrielle', 'Semestrielle'),
        ('annuelle', 'Annuelle'),
    ]

    extincteur = models.ForeignKey('Extincteur', on_delete=models.CASCADE)
    inspecteur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    type_inspection = models.CharField(max_length=15, choices=TYPE_INSPECTION_CHOICES)
    lieu = models.CharField(max_length=255)
    fiche_controle_verifiee = models.BooleanField(default=False)
    emplacement_correct = models.BooleanField(default=False)
    visible_accessible = models.BooleanField(default=False)
    plaque_lisible = models.BooleanField(default=False)
    signes_deterioration = models.BooleanField(default=False)
    pression_normale = models.BooleanField(default=False)
    mode_emploi_affiche = models.BooleanField(default=False)
    dommage_expose = models.BooleanField(default=False)
    observation = models.TextField(blank=True, null=True)
    prochaine_inspection = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Restriction des inspections annuelles
        if self.type_inspection == 'annuelle' and self.inspecteur.grade != 'Expert':
            raise ValueError("Seul un expert peut réaliser une inspection annuelle.")

        # Calcul de la prochaine date d'inspection
        if self.type_inspection == 'manuelle':
            self.prochaine_inspection = self.date + timedelta(days=30)
        elif self.type_inspection == 'trimestrielle':
            self.prochaine_inspection = self.date + timedelta(days=90)
        elif self.type_inspection == 'semestrielle':
            self.prochaine_inspection = self.date + timedelta(days=180)
        elif self.type_inspection == 'annuelle':
            self.prochaine_inspection = self.date + timedelta(days=365)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Inspection {self.type_inspection} - {self.extincteur.code} - {self.date}'

class Maintenance(models.Model):
    extincteur = models.ForeignKey('Extincteur', on_delete=models.CASCADE)
    expert = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    lieu = models.CharField(max_length=255)
    fiche_controle_verifiee = models.BooleanField(default=False)
    emplacement_correct = models.BooleanField(default=False)
    visible_accessible = models.BooleanField(default=False)
    plaque_lisible = models.BooleanField(default=False)
    signes_deterioration = models.BooleanField(default=False)
    pression_normale = models.BooleanField(default=False)
    mode_emploi_affiche = models.BooleanField(default=False)
    dommage_expose = models.BooleanField(default=False)
    observation = models.TextField(blank=True, null=True)
    prochaine_maintenance = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'Inspection {self.inspecteur} - {self.extincteur.code} - {self.date}'


class Notification(models.Model):
    date_notification = models.DateTimeField(auto_now_add=True)
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self):
        return f'Notification to {self.destinataire.email} on {self.date_notification}'


class RapportInspection(models.Model):
    date = models.DateField()
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='media/')






