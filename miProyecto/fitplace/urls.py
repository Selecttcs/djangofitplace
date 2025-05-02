from django.urls import path
from . import views

urlpatterns=[
    path('index/', views.index, name='index'),
    path('Login/', views.login, name='login'),
    path('CrearCuenta/', views.crearcuenta, name='crearcuenta'),
    path('RecuperarPass/', views.recuperarpass, name='recuperarpass'),
    path('RestablecerPass/', views.restablecerpass, name='restablecerpass'),
    path('Principal/', views.principal, name='principal'),
    path('Comunidad/', views.comunidad, name='comunidad'),
    path('Rutinas/', views.rutinas, name='rutinas'),
    path('Retroalimentacion/', views.retroalimentacion, name='retroalimentacion'),
    path('Nutricion/', views.nutricion, name='nutricion'),
    path('Perfil/', views.perfil, name='perfil'),
    path('CambiarCredenciales/', views.cambiarcredenciales, name='cambiarcredenciales'),
    path('Objetivos/', views.objetivos, name='objetivos'),
    path('Planes/', views.planes, name='planes'),
    path('Pago/', views.pago, name='pago'),
]