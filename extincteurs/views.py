from .models import Extincteur, RapportInspection, Inspection, Maintenance, Utilisateur
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from .forms import ExtincteurForm, SignUpForm, UtilisateurForm, CustomLoginForm, InspectionForm
from .forms import MaintenanceForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.utils.timezone import now
from datetime import datetime, timedelta
import random, time, json, os, zipfile
from reportlab.lib.pagesizes import letter, inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from io import BytesIO
import qrcode
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import red
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta


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
    if request.user.is_authenticated:
        user = request.user
    utilisateur = Utilisateur.objects.get(user=user)
    
    extincteur = get_object_or_404(Extincteur, code=code)
    qrcode_url = reverse('generate_qrcode', args=[extincteur.code])
    return render(request, 'details_extincteurs.html', {'extincteur': extincteur, 'qrcode_url': qrcode_url, 'utilisateur': utilisateur})


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


@login_required(login_url='/login')

def inspecter_extincteur(request, code):
    extincteur = get_object_or_404(Extincteur, code=code)
    if request.user.is_authenticated:
        user = request.user
    utilisateur = Utilisateur.objects.get(user=user)
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

            # En-tête avec le logo, la date et le titre
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']
            logo_path = finders.find('img/crtv.png')  # Remplacez par le chemin correct pour le logo

            if logo_path:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                story.append(logo)
            else:
                print("Logo file not found")
            
            # Date et titre du document
            title = Paragraph(f"Rapport d'Inspection de l'Extincteur {extincteur.code}", title_style)
            date = Paragraph(f"Date de l'inspection: {inspection.date.strftime('%d/%m/%Y')}", title_style)
            story.append(title)
            story.append(date)

            # Ajout d'une image d'extincteur
            img_extincteur_path = finders.find('img/e2.png')  # Image de l'extincteur (remplacer le chemin)
            if img_extincteur_path:
                img_extincteur = Image(img_extincteur_path, width=2*inch, height=2*inch)
                story.append(img_extincteur)
            
            story.append(Paragraph("<br/>", normal_style))  # Ajout d'un espace

            # Informations de l'inspection sous forme de tableau
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

           # Styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']

            # Définir un style personnalisé pour le titre
            red_title_style = ParagraphStyle(
                name='RedTitle',
                fontSize=14,
                textColor=red,
                parent=title_style
            )

            # Ajouter la section Observation
            observation_title = Paragraph("<br/>Observation", red_title_style)
            story.append(observation_title)

            story.append(Paragraph("<br/>", normal_style))

            # Table pour l'observation
            observation_table = Table([[inspection.observation]], colWidths=[7 * inch])  # Ajustez la largeur de la colonne si nécessaire
            observation_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, '#F11111'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                ('BACKGROUND', (0, 0), (-1, -1), '#FFFFFF'),  # Fond blanc pour le contraste
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alignement du texte à gauche
                ('BOX', (0, 0), (-1, -1), 1, '#0F0E0E'),  # Bordure du tableau
                ('ROUND', (0, 0), (-1, -1), 10),  # Bordures arrondies de 10 unités
            ]))

            # Ajuster la largeur des colonnes à leur contenu
            observation_table._argH[0] = None  # Hauteur automatique des lignes
            
            observation_table._argW[0] = observation_table.wrap(0, 0)[0]

            story.append(observation_table)
            
            story.append(Paragraph("<br/><br/>", normal_style))
            # Footer avec nom et poste de l'inspecteur
            story.append(Paragraph("<br/>", normal_style))  # Ajout d'un espace
            footer = Paragraph(f"Inspecteur: {utilisateur.prenom} {utilisateur.nom}, Poste: {utilisateur.poste}", title_style)
            story.append(footer)

            # Génération du PDF
            doc.build(story)
            buffer.seek(0)

            # Enregistrement du PDF
            rapport = RapportInspection()
            rapport.inspection = inspection
            rapport.date = inspection.date
            rapport.pdf.save(f"{extincteur.code}_{inspection.date.strftime('%Y-%m-%d')}.pdf", buffer, save=False)
            rapport.save()
            
            
            send_mail(
                subject="Prochaine maintenance d'extincteur",
                message=f"Bonjour {utilisateur.prenom},\n\nVotre prochaine maintenance pour l'extincteur {extincteur.code} est prévue pour le {inspection.prochaine_inspection.strftime('%d/%m/%Y')}.",
                from_email='propentatech@gmail.com',
                recipient_list=[utilisateur.email],
                fail_silently=False,
            )

            return redirect(reverse('details_extincteurs', args=[extincteur.code]))

    else:
        form = InspectionForm()

    return render(request, 'details_extincteurs.html', {'form': form, 'extincteur': extincteur, 'utilisateur': utilisateur})




@login_required(login_url='/login')
def maintenance_extincteur(request, code):
    extincteur = get_object_or_404(Extincteur, code=code)
    if request.user.is_authenticated:
        user = request.user
        utilisateur = Utilisateur.objects.get(user=user)
        
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.extincteur = extincteur
            maintenance.inspecteur = get_object_or_404(Utilisateur, user=request.user)
            maintenance.date = datetime.now()

            # Calcul de la prochaine inspection

            maintenance.prochaine_maintenance = maintenance.date + timedelta(days=365)

            maintenance.save()

            # Génération du fichier PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []

            # Styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']

            # En-tête avec le logo, la date et le titre
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']
            logo_path = finders.find('img/crtv.png')  # Remplacez par le chemin correct pour le logo

            if logo_path:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                story.append(logo)
            else:
                print("Logo file not found")
            
            # Date et titre du document
            title = Paragraph(f"Rapport de maintenance de l'Extincteur {extincteur.code}", title_style)
            date = Paragraph(f"Date de maintenance: {maintenance.date.strftime('%d/%m/%Y')}", title_style)
            story.append(title)
            story.append(date)

            # Ajout d'une image d'extincteur
            img_extincteur_path = finders.find('img/e2.png')  # Image de l'extincteur (remplacer le chemin)
            if img_extincteur_path:
                img_extincteur = Image(img_extincteur_path, width=2*inch, height=2*inch)
                story.append(img_extincteur)
            
            story.append(Paragraph("<br/>", normal_style))  # Ajout d'un espace

            # Informations de l'inspection
            content = [
                ['Date de maintenance', str(maintenance.date.strftime('%Y-%m-%d'))],
                ['Lieu', maintenance.lieu],
                ['Un contrôle visuel de l’état des extincteurs, à l’intérieur et à l’extérieur ?', 'Oui' if maintenance.fiche_controle_verifiee else 'Non'],
                ['Emplacement changé ?', 'Oui' if maintenance.emplacement_correct else 'Non'],
                ['Visible et accessible ?', 'Oui' if maintenance.visible_accessible else 'Non'],
                ['Un contrôle du système de sécurité et des éléments qui composent l’extincteur (tubes, lance, percuteur…) ?', 'Oui' if maintenance.plaque_lisible else 'Non'],
                ['Une vérification du niveau de l’eau ou de la poudre ?', 'Oui' if maintenance.signes_deterioration else 'Non'],
                ['Un graissage et l’entretien des pièces mobiles de l’extincteur ?', 'Oui' if maintenance.pression_normale else 'Non'],
                ['Un test de bon fonctionnement de la gâchette ?', 'Oui' if maintenance.mode_emploi_affiche else 'Non'],
                ['Un remplacement des joints d’étanchéité ?', 'Oui' if maintenance.dommage_expose else 'Non'],
                ['Observation', maintenance.observation],
                ['Prochaine maintenance', str(maintenance.prochaine_maintenance.strftime('%Y-%m-%d')) if maintenance.prochaine_maintenance else 'Non défini'],
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
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']

            # Définir un style personnalisé pour le titre
            red_title_style = ParagraphStyle(
                name='RedTitle',
                fontSize=14,
                textColor=red,
                parent=title_style
            )

            # Ajouter la section Observation
            observation_title = Paragraph("<br/>Observation de maintenance", red_title_style)
            story.append(observation_title)

            story.append(Paragraph("<br/>", normal_style))

            # Table pour l'observation
            observation_table = Table([[maintenance.observation]], colWidths=[7 * inch])  # Ajustez la largeur de la colonne si nécessaire
            observation_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, '#111010'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                ('BACKGROUND', (0, 0), (-1, -1), '#FFFFFF'),  # Fond blanc pour le contraste
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alignement du texte à gauche
                ('BOX', (0, 0), (-1, -1), 1, '#0F0E0E'),  # Bordure du tableau
                ('ROUND', (0, 0), (-1, -1), 10),  # Bordures arrondies de 10 unités
            ]))

            # Ajuster la largeur des colonnes à leur contenu
            observation_table._argH[0] = None  # Hauteur automatique des lignes
            
            observation_table._argW[0] = observation_table.wrap(0, 0)[0]

            story.append(observation_table)

            story.append(Paragraph("<br/><br/>", normal_style))
            # Footer avec nom et poste de l'inspecteur
            story.append(Paragraph("<br/>", normal_style))  # Ajout d'un espace
            footer = Paragraph(f"Maintenancier: {utilisateur.prenom} {utilisateur.nom}", title_style)
            story.append(footer)
            
            # Génération du PDF
            doc.build(story)
            buffer.seek(0)

            # Enregistrement du PDF
            rapport = RapportInspection()
            rapport.inspection = maintenance
            rapport.date = maintenance.date
            rapport.pdf.save(f"{extincteur.code}_{maintenance.date}.pdf", buffer, save=False)
            rapport.save()
            
            
            
            send_mail(
                subject="Prochaine maintenance d'extincteur",
                message=f"Bonjour {utilisateur.prenom},\n\nVotre prochaine maintenance pour l'extincteur {extincteur.code} est prévue pour le {maintenance.prochaine_maintenance.strftime('%d/%m/%Y')}.",
                from_email='propentatech@gmail.com',
                recipient_list=[utilisateur.email],
                fail_silently=False,
            )

            return redirect(reverse('details_extincteurs', args=[extincteur.code]))

    else:
        form = InspectionForm()

    return render(request, 'details_extincteurs.html', {'form': form, 'extincteur': extincteur, 'utilisateur': utilisateur})







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
