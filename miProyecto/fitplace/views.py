from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

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
        sexo = request.POST.get('sexo')  # Se asegura que sea 'sexo' para que coincida con el form

        # Depuración: Ver los datos recibidos del formulario
        print(f"POST recibido: Nombre_completo: {nombre_completo}, Correo: {correo_electronico}, Contraseña: {contrasena}, Edad: {edad}, Peso: {peso}, Estatura: {estatura}, Sexo: {sexo}")

        # Validar que las contraseñas coincidan
        if contrasena != confirmar_contrasena:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('crearcuenta')

        # Validar que sexo tenga un valor válido
        if not sexo or sexo not in ['M', 'F', 'O']:  # Ajusta según los valores permitidos en tu select
            messages.error(request, "Debe seleccionar un género válido.")
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

            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('login')

        except Exception as e:
            print(f"Error al crear la cuenta: {e}")
            messages.error(request, f"Hubo un error al crear la cuenta: {e}")
            return redirect('crearcuenta')

    return render(request, 'fitplace/CrearCuenta.html')
    
def recuperarpass(request):
    context={}
    return render(request,'fitplace/RecuperarPass.html', context)

def restablecerpass(request):
    context={}
    return render(request,'fitplace/RestablecerPass.html', context)    

def rutinas(request):
    


    context={}
    return render(request,'fitplace/Rutinas.html', context)    
    
def principal(request):
    context={}
    return render(request,'fitplace/Principal.html', context)    
    
def comunidad(request):
    #Aqui rescatamos la data de la base de datos de la tabla publicacion
    with connection.cursor() as cursor:
        cursor.execute("""SELECT TITULO, MENSAJE, FECHA FROM ADMIN.PUBLICACION ORDER BY FECHA DESC""")
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
                INSERT INTO ADMIN.PUBLICACION (TITULO, MENSAJE, FECHA)
                VALUES (%s, %s, SYSDATE)
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


    
def retroalimentacion(request):
    context={}
    return render(request,'fitplace/retroalimentacion.html', context)   

def nutricion(request):
    usuario_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EDAD, ESTATURA, PESO, SEXO, OBJETIVO
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :id_usuario
        """, {'id_usuario': usuario_id})
        user_data = cursor.fetchone()

    if user_data:
        edad = int(user_data[0])
        estatura_metros = float(user_data[1])  # en metros
        peso = float(user_data[2])             # en kg
        sexo = user_data[3]
        objetivo = user_data[4] or ''          # puede ser None

        estatura_cm = estatura_metros * 100

        # Fórmula Harris-Benedict para TMB
        if sexo.upper() == 'M':
            tmb = 10 * peso + 6.25 * estatura_cm - 5 * edad + 5
        else:
            tmb = 10 * peso + 6.25 * estatura_cm - 5 * edad - 161

        # Ajuste de actividad moderada
        calorias_base = tmb * 1.55

        # Ajustar calorías y macros según objetivo
        objetivo = objetivo.lower()
        proteina_extra = 0
        ajuste_calorias = 0

        if 'masa muscular' in objetivo:
            ajuste_calorias = 1.20  # +20%
            proteina_extra = 0.5    # +0.5 g/kg proteína
        elif 'perdida' in objetivo or 'grasa' in objetivo:
            ajuste_calorias = 0.80  # -20%
            proteina_extra = 0.5
        elif 'fuerza' in objetivo:
            ajuste_calorias = 1.15  # +15%
            proteina_extra = 0.4
        elif 'flexibilidad' in objetivo:
            ajuste_calorias = 1.0   # mantenimiento
            proteina_extra = 0.2
        else:
            ajuste_calorias = 1.0   # por defecto mantenimiento

        calorias = calorias_base * ajuste_calorias
        proteinas = peso * (2 + proteina_extra)  # base 2g/kg + extra según objetivo
        grasas = peso * 1   # constante para simplicidad
        calorias_proteina = proteinas * 4
        calorias_grasa = grasas * 9
        carbohidratos = (calorias - (calorias_proteina + calorias_grasa)) / 4

        vitaminas_mg = {
            "Vitamina A": 900 if sexo.upper() == 'M' else 700,
            "Vitamina C": 90 if sexo.upper() == 'M' else 75,
            "Vitamina D": 20,
            "Vitamina E": 15,
        }

        context = {
            'calorias': f"{round(calorias)} kcal",
            'grasas': f"{round(grasas)} g",
            'proteinas': f"{round(proteinas)} g",
            'carbohidratos': f"{round(carbohidratos)} g",
            'vitaminas': vitaminas_mg,
            'objetivo': objetivo.title() if objetivo else 'No definido',
        }
    else:
        context = {}

    return render(request, 'fitplace/nutricion.html', context)


def perfil(request):
    usuario_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT NOMBRE_COMPLETO, CORREO_ELECTRONICO, PESO, ESTATURA, EDAD, SEXO, OBJETIVO
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :id_usuario
        """, {'id_usuario': usuario_id})
        user_data = cursor.fetchone()

    if user_data:
        nombre = user_data[0]
        correo = user_data[1]
        peso = user_data[2]
        estatura = user_data[3]
        edad = user_data[4]
        sexo = user_data[5]
        objetivo = user_data[6]  # Asegúrate que tienes ese campo en la tabla

        # Convertir sexo 'M' o 'F' a texto
        if sexo.upper() == 'M':
            genero_texto = 'Masculino'
        elif sexo.upper() == 'F':
            genero_texto = 'Femenino'
        else:
            genero_texto = 'Otro'

        context = {
            'nombre': nombre,
            'correo': correo,
            'peso': peso,
            'estatura': estatura,
            'edad': edad,
            'genero': genero_texto,
            'objetivo': objetivo if objetivo else 'No definido'
        }
    else:
        context = {}

    return render(request, 'fitplace/Perfil.html', context)


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
    if request.method == "POST":
        objetivo = request.POST.get("objetivo")
        usuario_id = request.session.get('user_id')

        if usuario_id and objetivo:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE USUARIO
                        SET OBJETIVO = :objetivo
                        WHERE ID_USUARIO = :usuario_id
                    """, {'objetivo': objetivo, 'usuario_id': usuario_id})
                messages.success(request, "Objetivo guardado correctamente.")
            except Exception as e:
                print("Error al guardar objetivo:", e)
                messages.error(request, "Ocurrió un error al guardar tu objetivo.")
        else:
            messages.error(request, "Por favor selecciona un objetivo.")

        return redirect('objetivos')  # O a donde quieras redirigir tras guardar

    # Si es GET, solo renderiza la página con el form
    return render(request, 'fitplace/Objetivos.html')

def planes(request):
    context={}
    return render(request,'fitplace/Planes.html', context)  

def pago(request):
    context={}
    return render(request,'fitplace/Pago.html', context) 