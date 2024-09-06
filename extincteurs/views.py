from .models import *
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
import random, time
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from .models import Extincteur
from .forms import ExtincteurForm
import zipfile
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from .models import RapportInspection, Inspection
from datetime import datetime
from .forms import SignUpForm
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from .models import Utilisateur
from .forms import UtilisateurForm
from django.shortcuts import render
from django.db.models import Count
from .models import Utilisateur, Extincteur, Inspection, Maintenance, RapportInspection
from django.utils.timezone import now
from datetime import timedelta
from django.db.models.functions import ExtractMonth




# USER VIEWS

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Utilisateur
from .forms import CustomLoginForm

def custom_login_view(request):
    form = CustomLoginForm()
    display_error = False
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            try:
                # Essaie avec matricule
                user = Utilisateur.objects.get(matricule=identifier).user
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    if next_url:
                        return redirect(next_url)
                    return redirect('home')

            except Utilisateur.DoesNotExist:
                # Essaie avec téléphone
                try:
                    user = Utilisateur.objects.get(tel=identifier).user
                    user = authenticate(request, username=user.username, password=password)
                    if user is not None:
                        login(request, user)
                        if next_url:
                            return redirect(next_url)
                        return redirect('home')
                except Utilisateur.DoesNotExist:
                    # Essaie avec email
                    try:
                        user = Utilisateur.objects.get(email=identifier).user
                        user = authenticate(request, username=user.username, password=password)
                        if user is not None:
                            login(request, user)
                            if next_url:
                                return redirect(next_url)
                            return redirect('home')
                    except Utilisateur.DoesNotExist:
                        # Essaie avec nom
                        try:
                            user = Utilisateur.objects.get(nom=identifier).user
                            user = authenticate(request, username=user.username, password=password)
                            if user is not None:
                                login(request, user)
                                if next_url:
                                    return redirect(next_url)
                                return redirect('home')
                        except Utilisateur.DoesNotExist:
                            display_error = True

    context = {
        'form': form,
        'display_error': display_error,
        'next': next_url
    }

    return render(request, 'login.html', context)



def signup(request):
    if request.method == 'POST':
        matricule = request.POST['matricule']
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        email = request.POST['email']
        tel = request.POST['tel']
        poste = request.POST['poste']
        type_utilisateur = request.POST['type_utilisateur']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Vérification des mots de passe
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'signup.html', {
                'matricule': matricule,
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'tel': tel,
                'poste': poste,
                'type_utilisateur': type_utilisateur,
            })

        # Vérifie si l'utilisateur existe déjà
        if User.objects.filter(username=matricule).exists():
            messages.error(request, "Cet utilisateur existe déjà.")
            return redirect('signup')

        # Création de l'utilisateur
        user = User.objects.create_user(username=matricule, password=password, email=email)
        Utilisateur.objects.create(user=user, matricule=matricule, nom=nom, prenom=prenom, email=email, tel=tel, poste=poste, type_utilisateur=type_utilisateur)
        messages.success(request, "Votre compte a été créé avec succès.")
        return redirect('home')

    return render(request, 'signup.html')

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('login')


def init(request):
    return render(request, 'init.html')

@login_required(login_url='/login')
def home(request):
    if request.user.is_authenticated:
        user = request.user
        utilisateur = Utilisateur.objects.get(user=user)
        context = {
            'utilisateur': utilisateur
        }
    else:
        context = {}
    return render(request, 'home.html', context)


@login_required(login_url='/login')
def types_extincteurs(request):
    return render(request, 'types_extincteurs.html')



def extincteurs(request, type_extincteur):
    extincteurs = Extincteur.objects.filter(type_extincteur=type_extincteur)
    print(f"Type d'extincteur demandé : {type_extincteur}")
    print(f"Extincteurs trouvés : {list(extincteurs)}")
    return render(request, 'extincteurs.html', {'extincteurs': extincteurs, 'type_extincteur': type_extincteur})


@login_required(login_url='/login')
def details_extincteurs(request, code):
    extincteur = get_object_or_404(Extincteur, code=code)
    qrcode_url = reverse('generate_qrcode', args=[extincteur.code])
    return render(request, 'details_extincteurs.html', {'extincteur': extincteur, 'qrcode_url': qrcode_url})


@login_required(login_url='/login')
def contact(request):
    return render(request, 'contact.html')   


@login_required(login_url='/login')
def support(request):
    return render(request, 'support.html')


@login_required(login_url='/login')
def generate_qrcode(request, code):
    extincteur = get_object_or_404(Extincteur, code=code)
    
    # Préparer les données à inclure dans le QR code
    qr_data = (
        f"Code: {extincteur.code}\n"
        f"Type: {extincteur.get_type_extincteur_display()}\n"
        f"Classe: {extincteur.get_classe_display()}\n"
        f"Date d'achat: {extincteur.date_achat}\n"
        f"Localisation: {extincteur.localisation}"
    )
    
    # Générer le QR code avec une taille plus petite
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,  # Réduit la taille du QR code
        border=2,    # Réduit la bordure
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Sauvegarder l'image dans un buffer mémoire
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Retourner l'image comme réponse HTTP
    return HttpResponse(buffer, content_type="image/png")


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from reportlab.lib.pagesizes import letter, inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from io import BytesIO
from datetime import datetime, timedelta
from django.contrib.staticfiles import finders

from .models import Extincteur, Inspection, RapportInspection
from .forms import InspectionForm
@login_required(login_url='/login')
def inspecter_extincteur(request, code):
    extincteur = get_object_or_404(Extincteur, code=code)

    if request.method == 'POST':
        form = InspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.extincteur = extincteur
            inspection.inspecteur = get_object_or_404(Utilisateur, user=request.user)
            inspection.date = datetime.now()

            # Vérification du type d'inspection
            utilisateur = inspection.inspecteur
            if inspection.type_inspection == 'annuelle' and utilisateur.type_utilisateur != 'expert':
                # Ajouter un message d'erreur et rediriger
                messages.error(request, "Seuls les utilisateurs de type expert peuvent réaliser des inspections annuelles.")
                return redirect(request.META.get('HTTP_REFERER', 'details_extincteur.html'))

            # Calcul de la prochaine inspection
            if inspection.type_inspection == 'manuelle':
                inspection.prochaine_inspection = inspection.date + timedelta(days=30)
            elif inspection.type_inspection == 'trimestrielle':
                inspection.prochaine_inspection = inspection.date + timedelta(days=90)
            elif inspection.type_inspection == 'semestrielle':
                inspection.prochaine_inspection = inspection.date + timedelta(days=180)
            elif inspection.type_inspection == 'annuelle':
                inspection.prochaine_inspection = inspection.date + timedelta(days=365)

            inspection.save()

            # Génération du fichier PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []

            # En-tête avec le logo
            logo_path = finders.find('img/crtv.png')
            if logo_path:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                story.append(logo)
            else:
                print("Logo file not found")

            # Styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']

            # Titre du document
            title = Paragraph(f"Rapport d'Inspection de l'Extincteur {extincteur.code}", title_style)
            story.append(title)

            # Informations de l'inspection
            content = [
                ['Date de l\'inspection', str(inspection.date)],
                ['Lieu', inspection.lieu],
                ['Fiche contrôle vérifiée', 'Oui' if inspection.fiche_controle_verifiee else 'Non'],
                ['Emplacement correct', 'Oui' if inspection.emplacement_correct else 'Non'],
                ['Visible et accessible', 'Oui' if inspection.visible_accessible else 'Non'],
                ['Plaque lisible', 'Oui' if inspection.plaque_lisible else 'Non'],
                ['Signes de détérioration', 'Oui' if inspection.signes_deterioration else 'Non'],
                ['Pression normale', 'Oui' if inspection.pression_normale else 'Non'],
                ['Mode d\'emploi affiché', 'Oui' if inspection.mode_emploi_affiche else 'Non'],
                ['Exposé à un dommage', 'Oui' if inspection.dommage_expose else 'Non'],
                ['Observation', inspection.observation],
                ['Prochaine inspection', str(inspection.prochaine_inspection) if inspection.prochaine_inspection else 'Non défini'],
            ]

            table = Table(content)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#d5d5d5'),
                ('GRID', (0, 0), (-1, -1), 1, '#000000'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONT', (0, 1), (-1, -1), 'Helvetica'),
            ]))
            story.append(table)

            # Génération du PDF
            doc.build(story)
            buffer.seek(0)

            # Enregistrement du PDF
            rapport = RapportInspection()
            rapport.inspection = inspection
            rapport.date = inspection.date
            rapport.pdf.save(f"{extincteur.code}_{inspection.date}.pdf", buffer, save=False)
            rapport.save()

            return redirect(reverse('details_extincteurs', args=[extincteur.code]))

    else:
        form = InspectionForm()

    return render(request, 'details_extincteur.html', {'form': form, 'extincteur': extincteur})



def gestion_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'gestion_utilisateurs.html', {'utilisateurs': utilisateurs})

def add_utilisateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            # Créer l'objet User associé
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data['email'],
                    password=password
                )

                # Créer l'objet Utilisateur avec le User associé
                utilisateur = form.save(commit=False)
                utilisateur.user = user  # Associer le User à l'Utilisateur
                utilisateur.save()

                messages.success(request, 'Utilisateur ajouté avec succès.')
                return redirect('gestion_utilisateurs')

            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout de l\'utilisateur : {str(e)}')
        else:
            messages.error(request, 'Erreur lors de l\'ajout de l\'utilisateur.')
    else:
        form = UtilisateurForm()

    utilisateurs = Utilisateur.objects.all()  # Charger les utilisateurs pour les afficher
    return render(request, 'gestion_utilisateurs.html', {'form': form, 'utilisateurs': utilisateurs})


def edit_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    if request.method == 'POST':
        form = UtilisateurForm(request.POST, instance=utilisateur)
        if form.is_valid():
            # Mettre à jour l'objet User associé
            utilisateur.user.username = form.cleaned_data['email']
            utilisateur.user.email = form.cleaned_data['email']
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                utilisateur.user.password = make_password(form.cleaned_data['password'])
            utilisateur.user.save()

            # Mettre à jour l'objet Utilisateur
            form.save()

            messages.success(request, 'Utilisateur modifié avec succès.')
            return redirect('gestion_utilisateurs')
        else:
            messages.error(request, 'Erreur lors de la modification de l\'utilisateur.')
    else:
        form = UtilisateurForm(instance=utilisateur)

    utilisateurs = Utilisateur.objects.all()  
    return render(request, 'gestion_utilisateurs.html', {'form': form, 'utilisateurs': utilisateurs})


def delete_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    utilisateur.user.delete()
    utilisateur.delete()
    messages.success(request, 'Utilisateur supprimé avec succès.')
    return redirect('gestion_utilisateurs')



def gestion_extincteurs(request):
    extincteurs = Extincteur.objects.all()
    return render(request, 'gestion_extincteurs.html', {'extincteurs': extincteurs})

def add_extincteur(request):
    if request.method == 'POST':
        form = ExtincteurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_extincteurs')
    else:
        form = ExtincteurForm()
        
    extincteurs = Extincteur.objects.all()  
       
    return render(request, 'gestion_extincteurs.html', {'form': form, 'extincteurs':extincteurs})

def edit_extincteur(request, extincteur_id):
    extincteur = get_object_or_404(Extincteur, code=extincteur_id)
    if request.method == 'POST':
        form = ExtincteurForm(request.POST, instance=extincteur)
        if form.is_valid():
            form.save()
            return redirect('gestion_extincteurs')
    else:
        form = ExtincteurForm(instance=extincteur)
    return render(request, 'edit_extincteur.html', {'form': form, 'extincteur': extincteur})

def delete_extincteur(request, extincteur_id):
    extincteur = get_object_or_404(Extincteur, code=extincteur_id)
    if request.method == 'POST':
        extincteur.delete()
        return redirect('gestion_extincteurs')
    return render(request, 'gestion_extincteurs.html', {'extincteur': extincteur})




def gestion_rapports(request):
    rapports = RapportInspection.objects.all()
    inspection_dates = Inspection.objects.values_list('date', flat=True).distinct()
    context = {
        'inspection_dates': inspection_dates,
        'rapports': rapports,
    }
    return render(request, 'rapports.html', context)






def stats_view(request):
    # Nombre total d'inspections
    total_inspections = Inspection.objects.count() 
    
    total_extincteurs = Extincteur.objects.count() 

    # Nombre total d'utilisateurs
    total_utilisateurs = Utilisateur.objects.count()

    # Dernière date d'inspection
    derniere_inspection = Inspection.objects.latest('date').date if total_inspections > 0 else "Aucune inspection"

    # Nombre total de rapports d'inspection
    total_rapports = RapportInspection.objects.count()

    # Statistiques d'inspection par mois
    inspections_par_mois = Inspection.objects.filter(date__year=now().year).annotate(month=ExtractMonth('date')).values('month').annotate(count=Count('id')).order_by('month')

    # Statistiques d'inspection par type
    inspections_par_type = Inspection.objects.values('type_inspection').annotate(count=Count('id'))

    context = {
        'total_inspections': total_inspections,
        'total_utilisateurs': total_utilisateurs,
        'derniere_inspection': derniere_inspection,
        'total_extincteurs': total_extincteurs,
        'total_rapports': total_rapports,
        'inspections_par_mois': inspections_par_mois,
        'inspections_par_type': inspections_par_type,
    }

    return render(request, 'stats.html', context)




def download_reports_view(request):
    if request.method == 'POST':
        selected_date = request.POST.get('inspection_date')
        
        if selected_date:
            try:
                # Adapter le format ici pour correspondre au format attendu
                selected_date = datetime.strptime(selected_date, "%b. %d, %Y").date()
            except ValueError:
                return HttpResponse("Format de date incorrect.", status=400)
            
            rapports = RapportInspection.objects.filter(inspection__date=selected_date)
            
            if rapports.exists():
                # Création du fichier zip
                zip_filename = f"rapports_{selected_date}.zip"
                zip_filepath = os.path.join('media', zip_filename)

                with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
                    for rapport in rapports:
                        # Ajout des fichiers PDF au zip
                        zip_file.write(rapport.pdf.path, os.path.basename(rapport.pdf.path))
                
                # Retourner le fichier zip à l'utilisateur
                with open(zip_filepath, 'rb') as file:
                    response = HttpResponse(file.read(), content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                    return response

    # Si la date n'est pas sélectionnée ou aucun rapport n'existe
    return HttpResponse("Aucun rapport trouvé pour la date sélectionnée.", status=404)
