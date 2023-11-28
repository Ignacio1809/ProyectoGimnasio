from django.contrib import admin
from .models import Plan, Video, cliente, VideoView

class PlanAdmin(admin.ModelAdmin):
    list_display = ['nombre_plan']  # Ajusta los campos que quieras mostrar
    filter_horizontal = ('videos',)

# Otras clases admin si son necesarias...

class VideoViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'viewed')  # Ajusta los campos que quieras mostrar
    list_filter = ('viewed',)  # Agrega filtros si es necesario
    search_fields = ('user__username', 'video__url')  # Permite buscar por usuario y URL de video


admin.site.register(Plan, PlanAdmin)
admin.site.register(Video)
admin.site.register(cliente)
admin.site.register(VideoView, VideoViewAdmin)
