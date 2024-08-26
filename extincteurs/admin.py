from django.contrib import admin
from .models import Utilisateur, Extincteur, Inspection, Maintenance, Notification, RapportInspection

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'email', 'poste', 'type_utilisateur')
    search_fields = ('matricule', 'nom', 'prenom', 'email')

class ExtincteurAdmin(admin.ModelAdmin):
    list_display = ('code', 'type_extincteur', 'classe',  'date_achat', 'date_valid', 'localisation')
    search_fields = ('code', 'type_extincteur', 'localisation')

class InspectionAdmin(admin.ModelAdmin):
    list_display = ('date', 'type_inspection', 'extincteur', 'inspecteur')
    search_fields = ('date', 'type_inspection', 'extincteur__code', 'inspecteur__username')

class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'type_maintenance', 'extincteur', 'expert')
    search_fields = ('date', 'type_maintenance', 'extincteur__code', 'expert__username')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('date_notification', 'destinataire')
    search_fields = ('date_notification', 'destinataire__username')

class RapportInspectionAdmin(admin.ModelAdmin):
    list_display = ('inspection',)
    search_fields = ('inspection__id',)

admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Extincteur, ExtincteurAdmin)
admin.site.register(Inspection, InspectionAdmin)
admin.site.register(Maintenance, MaintenanceAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(RapportInspection, RapportInspectionAdmin)
