from django.urls import path
from . import views

urlpatterns=[
    path('index/', views.index, name='index'),
    path('Login/', views.login, name='login'),
    path('CrearCuenta/', views.crear_cuenta, name='crearcuenta'),
    path('RecuperarPass/', views.recuperarpass, name='recuperarpass'),
    path('RestablecerPass/', views.restablecerpass, name='restablecerpass'),
    path('Principal/', views.principal, name='principal'),
    path('Comunidad/', views.comunidad, name='comunidad'),
    path('like/', views.toggle_like, name='dar_like'),  
    path('Rutinas/', views.rutinas, name='rutinas'),
    path('Retroalimentacion/', views.retroalimentacion, name='retroalimentacion'),
    path('guardar-retroalimentacion/', views.guardar_retroalimentacion, name='guardar_retroalimentacion'),
    path('Nutricion/', views.nutricion, name='nutricion'),
    path('Perfil/', views.perfil, name='perfil'),
    path('CambiarCredenciales/', views.cambiarcredenciales, name='cambiarcredenciales'),
    path('CambiarCredencialesCode/', views.cambiarcredenciales, name='cambiarcredencialescode'),
    path('Objetivos/', views.objetivos, name='objetivos'),
    path('Planes/', views.planes, name='planes'),
    path('Pago/', views.pago, name='pago'),
    path('enviar_mensaje_chat/', views.enviar_mensaje_chat, name='enviar_mensaje_chat'),
    path('cargar_mensajes_chat/cliente/', views.cargar_mensajes_chat, name='cargar_mensajes_chat_cliente'),
    path('trainer/chats/', views.panel_entrenador_chats, name='panel_entrenador_chats'),
    path('cargar_mensajes_chat/entrenador/<int:cliente_id>/', views.cargar_mensajes_chat, name='cargar_mensajes_chat_entrenador'),
]