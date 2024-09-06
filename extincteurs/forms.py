from django import forms
from .models import Utilisateur, Extincteur
from django import forms
from django.contrib.auth.models import User
from .models import Utilisateur
from django import forms
from .models import Inspection

class CustomLoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Email, Phone, Name, or Matricule'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        required=True
    )


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirmer le mot de passe")

    class Meta:
        model = Utilisateur
        fields = ['matricule', 'nom', 'prenom', 'email', 'tel', 'poste', 'type_utilisateur']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_tel(self):
        tel = self.cleaned_data.get('tel')
        if Utilisateur.objects.filter(tel=tel).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return tel

    def clean_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = [
            'lieu','type_inspection', 'fiche_controle_verifiee', 'emplacement_correct', 
            'visible_accessible', 'plaque_lisible', 'signes_deterioration',
            'pression_normale', 'mode_emploi_affiche', 'dommage_expose', 'observation'
        ]
        widgets = {
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'class': 'form-control'}),
        }

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = [
            'lieu', 'fiche_controle_verifiee', 'emplacement_correct', 
            'visible_accessible', 'plaque_lisible', 'signes_deterioration',
            'pression_normale', 'mode_emploi_affiche', 'dommage_expose', 'observation'
        ]
        widgets = {
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'class': 'form-control'}),
        }

class UtilisateurForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, help_text="Required.")
    password_confirm = forms.CharField(widget=forms.PasswordInput, help_text="Enter the password again for confirmation.")

    class Meta:
        model = Utilisateur
        fields = ['matricule', 'nom', 'prenom', 'tel', 'email', 'poste', 'type_utilisateur','password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas !")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Création de l'utilisateur associé
        if not user.user:
            user.user = User.objects.create_user(
                username=self.cleaned_data['email'],  # Utiliser l'email comme nom d'utilisateur
                password=self.cleaned_data['password']
            )
        else:
            # Si l'utilisateur existe déjà, mettre à jour le mot de passe
            user.user.set_password(self.cleaned_data['password'])
            user.user.save()

        if commit:
            user.save()
        return user


class ExtincteurForm(forms.ModelForm):
    class Meta:
        model = Extincteur
        fields = ['type_extincteur', 'classe', 'date_achat', 'date_valid', 'localisation']
        widgets = {
            'type_extincteur': forms.Select(attrs={'class': 'form-control'}),
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'date_achat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_valid': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
        }

