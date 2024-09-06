
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', init, name='init'),
    path('login/', custom_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup, name='signup'),
    path('home/', home, name='home'),
    path('types_extincteurs/', types_extincteurs, name='types_extincteurs'),
    path('extincteurs/<str:type_extincteur>/', extincteurs, name='extincteurs'),
    path('details_extincteurs/<str:code>/', details_extincteurs, name='details_extincteurs'),
    path('generate_qrcode/<str:code>/', generate_qrcode, name='generate_qrcode'),
    path('contact/', contact, name='contact'),
    path('support/', support, name='support'),
    path('inspecter/<str:code>/', inspecter_extincteur, name='inspecter_extincteur'), 
    path('maintenance/<str:code>/', maintenance_extincteur, name='maintenance_extincteur'), 

    
    
    
    
    path('gestion_utilisateurs/', gestion_utilisateurs, name='gestion_utilisateurs'),
    path('add_utilisateur/', add_utilisateur, name='add_utilisateur'),
    path('edit_utilisateur/<int:utilisateur_id>/', edit_utilisateur, name='edit_utilisateur'),
    path('delete_utilisateur/<int:utilisateur_id>/', delete_utilisateur, name='delete_utilisateur'),
    
    
    
    path('gestion_extincteurs/', gestion_extincteurs, name='gestion_extincteurs'),
    path('extincteur/add/', add_extincteur, name='add_extincteur'),
    path('extincteur/edit/<str:extincteur_id>/', edit_extincteur, name='edit_extincteur'),
    path('extincteur/delete/<str:extincteur_id>/', delete_extincteur, name='delete_extincteur'),
    path('gestion_rapports/', gestion_rapports, name='gestion_rapports'), 
    path('download_reports/', download_reports_view, name='download_reports'),

    
    path('stats/', stats_view, name='stats'), 


]
