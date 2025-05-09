from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import check_password
# Create your views here.
import time

def index(request):
    context={}
    return render(request,'fitplace/index.html', context)

def login(request):
    if request.method == "POST":
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ID_USUARIO FROM "ADMIN"."USUARIO" 
                    WHERE CORREO_ELECTRONICO = :correo AND CONTRASENA = :contrasena
                """, {'correo': correo, 'contrasena': contrasena})
                user = cursor.fetchone()

                if user:
                    request.session['user_id'] = user[0]
                    return redirect('principal')
                else:
                    messages.error(request, "Correo o contraseña incorrectos.")
        except Exception as e:
            messages.error(request, f"Error al acceder a la base de datos: {e}")

    return render(request, 'fitplace/Login.html')

def crear_cuenta(request):
    if request.method == "POST":
        # Recoger datos del formulario
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        edad = request.POST.get('edad')
        peso = request.POST.get('peso')
        estatura = request.POST.get('estatura')
        genero = request.POST.get('genero')

        # Validar que las contraseñas coincidan
        if contrasena != confirmar_contrasena:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('crearcuenta')

        # Crear el insert a la base de datos
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO USUARIO (NOMBRE, CORREO, CONTRASENA, EDAD, PESO, ESTATURA, GENERO)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [nombre, correo, contrasena, edad, peso, estatura, genero])
            cursor.close()

            # Mostrar mensaje de éxito
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('login')
        
        except Exception as e:
            # Manejar cualquier error con la base de datos
            messages.error(request, f"Hubo un error al crear la cuenta: {e}")
            return redirect('CrearCuenta')

    return render(request, 'fitplace/CrearCuenta.html')
    
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
    # Obtener el ID del usuario actualmente logueado (o el que se usó para iniciar sesión)
    usuario_id = request.session.get('user_id')  # Asegúrate de que 'user_id' esté en la sesión tras el login

    # Realizar la consulta para obtener los datos del perfil
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT NOMBRE_COMPLETO, CORREO_ELECTRONICO, PESO, ESTATURA, EDAD, SEXO
            FROM ADMIN.USUARIO 
            WHERE ID_USUARIO = :id_usuario
        """, {'id_usuario': usuario_id})
        
        # Obtener los datos del usuario
        user_data = cursor.fetchone()

    if user_data:
        # Si encontramos los datos del usuario, pasarlos al contexto
        context = {
            'nombre': user_data[0],
            'correo': user_data[1],
            'peso': user_data[2],
            'estatura': user_data[3],
            'edad': user_data[4],
            'genero': user_data[5],
        }
    else:
        context = {}

    return render(request, 'fitplace/perfil.html', context)


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