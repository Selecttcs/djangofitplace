from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
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
        nombre_completo = request.POST.get('nombre')
        correo_electronico = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        edad = request.POST.get('edad')
        peso = request.POST.get('peso')
        estatura = request.POST.get('estatura')
        sexo = request.POST.get('sexo')

        # Depuración: Ver los datos recibidos del formulario
        print(f"POST recibido: Nombre_completo: {nombre_completo}, Correo: {correo_electronico}, Contraseña: {contrasena}, Edad: {edad}, Peso: {peso}, Estatura: {estatura}, Sexo: {sexo}")

        # Validar que las contraseñas coincidan
        if contrasena != confirmar_contrasena:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('crearcuenta')

        # Intentar realizar el insert a la base de datos
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO USUARIO (NOMBRE_COMPLETO, CORREO_ELECTRONICO, CONTRASENA, EDAD, PESO, ESTATURA, SEXO)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [nombre_completo, correo_electronico, contrasena, edad, peso, estatura, sexo])
            cursor.close()
            print("Cuenta creada exitosamente.")

            # Mostrar mensaje de éxito
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('login')
        
        except Exception as e:
            # Depuración: Mostrar el error en consola si ocurre
            print(f"Error al crear la cuenta: {e}")  # Depuración
            messages.error(request, f"Hubo un error al crear la cuenta: {e}")
            return redirect('crearcuenta')

    # Si el método no es POST, mostrar el formulario de creación de cuenta
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
    #Aqui rescatamos la data de la base de datos de la tabla publicacion
    with connection.cursor() as cursor:
        cursor.execute("""SELECT TITULO, MENSAJE FROM ADMIN.PUBLICACION""")
        publicacion = cursor.fetchall()

    context={'publicacion': publicacion
    }

    # Aquí enviamos con el metodo post la publicacion a la base de datos
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        mensaje = request.POST.get('mensaje')
        print(f"POST recibido: Titulo: {titulo}, Mensaje: {mensaje}")

        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO ADMIN.PUBLICACION (TITULO, MENSAJE)
                VALUES (%s, %s)
            """, [titulo, mensaje])
            cursor.close()
            print("Publicación subida correctamente.")

            # Mostrar mensaje de éxito
            messages.success(request, "Publicación subida correctamente.")
            return redirect('comunidad')
        
        except Exception as e:
            # Depuración: Mostrar el error en consola si ocurre
            print(f"Error al querer subir una publicacion: {e}")  # Depuración
            messages.error(request, f"Error al querer subir una publicacion: {e}")
            return redirect('comunidad')



    return render(request,'fitplace/Comunidad.html', context)   

def rutinas(request):
    # Realizamos la consulta a la base de datos para obtener los ejercicios
    with connection.cursor() as cursor:
        cursor.execute("""SELECT NOMBRE_EJERCICIO, DESCRIPCION, TIPO_EJERCICIO FROM ADMIN.EJERCICIO""")
        ejercicios = cursor.fetchall()

    # Pasamos los ejercicios al contexto
    context = {
        'ejercicios': ejercicios
    }

    return render(request, 'fitplace/Rutinas.html', context)
    
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

    usuario_id = request.session.get('user_id')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT CORREO_ELECTRONICO 
            FROM "ADMIN"."USUARIO" 
            WHERE ID_USUARIO = :usuario_id
        """, {'usuario_id': usuario_id})
        correo_electronico = cursor.fetchone()[0]  

    if request.method == "POST":
        nombre = request.POST.get('nombre')
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        usuario_id = request.session.get('user_id')

        # Verificar si las contraseñas coinciden
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('cambiarcredenciales')

        try:
            # Crear la consulta para actualizar el nombre y la contraseña
            with connection.cursor() as cursor:
                if nombre and nueva_contrasena:
                    # Si ambos nombre y contraseña son proporcionados, actualizamos ambos
                    cursor.execute("""
                        UPDATE "ADMIN"."USUARIO"
                        SET NOMBRE_COMPLETO = :nombre, CONTRASENA = :nueva_contrasena
                        WHERE ID_USUARIO = :usuario_id
                    """, {'nombre': nombre, 'nueva_contrasena': nueva_contrasena, 'usuario_id': usuario_id})
                elif nombre:
                    # Si solo el nombre es proporcionado, actualizamos solo el nombre
                    cursor.execute("""
                        UPDATE "ADMIN"."USUARIO"
                        SET NOMBRE_COMPLETO = :nombre
                        WHERE ID_USUARIO = :usuario_id
                    """, {'nombre': nombre, 'usuario_id': usuario_id})
                elif nueva_contrasena:
                    # Si solo la contraseña es proporcionada, actualizamos solo la contraseña
                    cursor.execute("""
                        UPDATE "ADMIN"."USUARIO"
                        SET CONTRASENA = :nueva_contrasena
                        WHERE ID_USUARIO = :usuario_id
                    """, {'nueva_contrasena': nueva_contrasena, 'usuario_id': usuario_id})

            # Mensaje de éxito
            messages.success(request, "¡Sus credenciales han sido modificadas correctamente!")
            return redirect('perfil')

        except Exception as e:
            messages.error(request, f"Error al cambiar las credenciales: {e}")
            return redirect('cambiarcredenciales')

    context = {
        'correo': correo_electronico
    }
    return render(request, 'fitplace/CambiarCredenciales.html', context)


def objetivos(request):
    context={}
    return render(request,'fitplace/Objetivos.html', context)  

def planes(request):
    context={}
    return render(request,'fitplace/Planes.html', context)  

def pago(request):
    context={}
    return render(request,'fitplace/Pago.html', context) 