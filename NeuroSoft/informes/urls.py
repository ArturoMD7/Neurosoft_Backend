from django.urls import path
from . import views

urlpatterns = [
    path('generar-informe/<int:resultado_id>/', views.generar_informe_pdf, name='generar_informe_pdf'),
]
