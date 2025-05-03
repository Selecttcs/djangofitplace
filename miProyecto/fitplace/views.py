from django.shortcuts import render
from django.db import connection
# Create your views here.


def index(request):
    context={}
    return render(request,'fitplace/index.html', context)

def login(request):
    context={}
    return render(request,'fitplace/Login.html', context)

def crearcuenta(request):
    context={}
    return render(request,'fitplace/CrearCuenta.html', context)
    
def recuperarpass(request):
    context={}
    return render(request,'fitplace/RecuperarPass.html', context)

def restablecerpass(request):
    context={}
    return render(request,'fitplace/RestablecerPass.html', context)    
    
def principal(request):
    context={}
    return render(request,'fitplace/Principal.html', context)    
    
def comunidad(request):
    context={}
    return render(request,'fitplace/Comunidad.html', context)   

def rutinas(request):
    context={}
    return render(request,'fitplace/Rutinas.html', context)   
    
def retroalimentacion(request):
    context={}
    return render(request,'fitplace/retroalimentacion.html', context)   

def nutricion(request):
    context={}
    return render(request,'fitplace/nutricion.html', context)  

def perfil(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT ID_USUARIO, NOMBRE_COMPLETO, EDAD FROM USUARIO")
        rows = cursor.fetchall()

    usuarios = [{'id': r[0], 'nombre': r[1], 'correo': r[2]} for r in rows]

    return render(request, 'fitplace/perfil.html', {'usuarios': usuarios})

def cambiarcredenciales(request):
    context={}
    return render(request,'fitplace/CambiarCredenciales.html', context)  

def objetivos(request):
    context={}
    return render(request,'fitplace/Objetivos.html', context)  

def planes(request):
    context={}
    return render(request,'fitplace/Planes.html', context)  

def pago(request):
    context={}
    return render(request,'fitplace/Pago.html', context) 