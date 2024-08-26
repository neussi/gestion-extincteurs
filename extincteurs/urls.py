
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
    
    
    
    
    path('gestion_utilisateurs/', gestion_utilisateurs, name='gestion_utilisateurs'),
    path('add_utilisateur/', add_utilisateur, name='add_utilisateur'),
    path('edit_utilisateur/<int:utilisateur_id>/', edit_utilisateur, name='edit_utilisateur'),
    path('delete_utilisateur/<int:utilisateur_id>/', delete_utilisateur, name='delete_utilisateur'),

]
