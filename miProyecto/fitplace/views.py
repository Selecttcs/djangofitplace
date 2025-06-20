import random
import smtplib
import ssl
import unicodedata
import time
import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.db import connection
from email.message import EmailMessage

# Create your views here.

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
                    os.system("cls")
                    print('Credenciales correctas, redirigiendo a la pantalla principal')
                    return redirect('principal')
                else:
                    os.system("cls")
                    print('Correo o contraseña incorrectos.')
                    messages.error(request, "Correo o contraseña incorrectos.")
        except Exception as e:
            os.system("cls")
            messages.error(request, f"Error al acceder a la base de datos: {e}")
            print('Error al acceder a la Base de datos.')

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

##Recuperar PASS 

def recuperarpass(request):
    mostrar_modal = False

    if request.method == 'POST' and 'correo' in request.POST and 'codigo' not in request.POST:
        # Enviar código por correo
        correo = request.POST.get('correo')
        codigo = str(random.randint(100000, 999999))
        request.session['codigo_recuperacion'] = codigo
        request.session['correo_recuperacion'] = correo

        try:
            msg = EmailMessage()
            msg.set_content(f'Tu código de recuperación es: {codigo}')
            msg['Subject'] = 'Código de recuperación de contraseña'
            msg['From'] = 'fitplac3@gmail.com'
            msg['To'] = correo

            context = ssl.create_default_context()

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login('fitplac3@gmail.com', 'zcydzrcoojstwznc')
                server.send_message(msg)

            messages.success(request, "Código enviado a tu correo.")
            mostrar_modal = True  # Mostrar modal para ingresar código
        except Exception as e:
            messages.error(request, f"Error al enviar correo: {e}")

    elif request.method == 'POST' and 'codigo' in request.POST:
        # Validar código ingresado
        codigo_ingresado = request.POST.get('codigo')
        codigo_enviado = request.session.get('codigo_recuperacion')

        # Debug: imprimir códigos para revisar
        print(f"codigo ingresado: {codigo_ingresado}")
        print(f"codigo enviado: {codigo_enviado}")

        if codigo_ingresado == codigo_enviado:
            return redirect('restablecerpass')
        else:
            messages.error(request, "Código incorrecto.")
            mostrar_modal = True

    return render(request, 'fitplace/RecuperarPass.html', {'mostrar_modal': mostrar_modal})




def restablecerpass(request):
    if request.method == 'POST':
        nueva_pass = request.POST.get('nueva_pass')
        repetir_pass = request.POST.get('repetir_pass')
        correo = request.session.get('correo_recuperacion')

        print(f"nueva_pass: {nueva_pass}")
        print(f"repetir_pass: {repetir_pass}")
        print(f"correo en sesión: {correo}")

        if not nueva_pass or not repetir_pass:
            messages.error(request, "Debes completar ambos campos de contraseña.")
        elif nueva_pass != repetir_pass:
            messages.error(request, "Las contraseñas no coinciden.")
        elif correo:
            try:
                nueva_pass_str = str(nueva_pass) if nueva_pass is not None else ''
                correo_str = str(correo) if correo is not None else ''

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE USUARIO
                            SET CONTRASENA = :1
                            WHERE CORREO_ELECTRONICO = :2
                        """, [nueva_pass_str, correo_str])
                        filas_afectadas = cursor.rowcount
                        print(f"Filas afectadas por el UPDATE: {filas_afectadas}")

                    if filas_afectadas == 0:
                        messages.error(request, "No se encontró usuario con ese correo.")
                    else:
                        print("Contraseña actualizada con éxito, redirigiendo...")
                        messages.success(request, "Contraseña actualizada correctamente.")
                        request.session.pop('correo_recuperacion', None)
                        request.session.pop('codigo_recuperacion', None)
                        return redirect('login')

            except Exception as e:
                print(f"Exception al actualizar contraseña: {e}")
                messages.error(request, f"Error al actualizar contraseña: {e}")
        else:
            messages.error(request, "No se encontró correo asociado en la sesión.")

    return render(request, 'fitplace/RestablecerPass.html')



def normalize_text(text):
    if not text:
        return ''
    text = text.strip().lower()
    # Eliminar tildes
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    # Eliminar espacios internos para mapear bien
    text = text.replace(' ', '')
    return text

def rutinas(request):
    
    usuario_id = request.session.get('user_id')
    print(f"Usuario en sesión: {usuario_id}")

    if not usuario_id:
        print("No hay usuario en sesión, redirigiendo a login...")
        return redirect('login')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre_completo FROM usuario WHERE id_usuario = :id", {'id': usuario_id})
        resultado = cursor.fetchone()
        nombre_usuario = resultado[0] if resultado else "Desconocido"
    # Validación del tipo de plan
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PLAN_ID_PLAN
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :usuario_id
        """, {'usuario_id': usuario_id})
        row = cursor.fetchone()
    plan_id = row[0] if row else None

    id_entrenador = 666575 #temporal

     # Consulta de mensajes del chat (entre usuario y entrenador)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ID_CHAT, MENSAJE, FECHA, NOMBRE_EMISOR, ID_EMISOR, ID_RECEPTOR
            FROM CHAT_PERSONAL_TRAINER
            WHERE (ID_EMISOR = :usuario_id AND ID_RECEPTOR = :id_entrenador)
            OR (ID_EMISOR = :id_entrenador AND ID_RECEPTOR = :usuario_id)
            ORDER BY FECHA ASC
        """, {'usuario_id': usuario_id, 'id_entrenador': id_entrenador})
        chat_data = cursor.fetchall()
        columns_chat = [col[0] for col in cursor.description]

    chat = [dict(zip(columns_chat, row)) for row in chat_data]

        # 🔽 BLOQUE PARA INSERTAR MENSAJE NUEVO EN CHAT
    if request.method == 'POST' and 'mensaje_chat' in request.POST:
        mensaje_texto = request.POST.get('mensaje_chat')
        print(f'Mensaje enviado: {mensaje_texto}')
        if mensaje_texto.strip():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO chat_personal_trainer (id_emisor, id_receptor, nombre_emisor, mensaje, fecha)
                    VALUES (:id_emisor, :id_receptor, :nombre_emisor, :mensaje, SYSDATE)
                 """, {
                    'id_emisor': usuario_id,
                    'id_receptor': id_entrenador,
                    'nombre_emisor': nombre_usuario,
                    'mensaje': mensaje_texto
                })
        return redirect(request.path)
    # 🔼 FIN BLOQUE CHAT

    with connection.cursor() as cursor:
        # Obtener objetivo crudo del usuario
        cursor.execute("SELECT objetivo FROM usuario WHERE id_usuario = :id", {'id': usuario_id})
        resultado = cursor.fetchone()
        objetivo_raw = resultado[0] if resultado else None
        print(f"Objetivo del usuario (raw): {objetivo_raw}")

        mapa_objetivos = {
            'aumentodefuerza': 'fuerza',
            'perdidadegrasa': 'perdida grasa',
            'masamuscular': 'masa muscular',
            'flexibilidad': 'flexibilidad',
        }

        objetivo_normalizado = normalize_text(objetivo_raw)
        print(f"Objetivo del usuario (normalizado): {objetivo_normalizado}")

        objetivo = mapa_objetivos.get(objetivo_normalizado, None)

        if not objetivo:
            context = {
                'mensaje': 'No tienes un objetivo definido o no soportado. Por favor, establece uno válido para generar rutinas.',
                'tiene_rutina': False,
                'rutina_por_dia_lista': [],
                'chat': chat
            }
            print("Objetivo no soportado o no definido, renderizando template sin rutina.")
            template = 'fitplace/Rutinas.html' if plan_id == 1 else 'fitplace/EliteFit/RutinasELITE.html'
            return render(request, template, context)

        # Buscar rutina para el objetivo
        cursor.execute("SELECT id_rutina, nombre_rutina, descripcion FROM rutina WHERE objetivo = :obj", {'obj': objetivo})
        rutina = cursor.fetchone()
        print(f"Rutina encontrada para el objetivo: {rutina}")

        if not rutina:
            context = {
                'mensaje': f'No existe una rutina disponible para el objetivo \"{objetivo}\".',
                'tiene_rutina': False,
                'rutina_por_dia_lista': [],
                'chat': chat
            }
            print("No hay rutina para ese objetivo.")
            template = 'fitplace/Rutinas.html' if plan_id == 1 else 'fitplace/EliteFit/RutinasELITE.html'
            return render(request, template, context)

        id_rutina, nombre_rutina, descripcion_rutina = rutina

        # Verificar rutina asignada
        cursor.execute("SELECT id_rutina_asignada FROM usuario WHERE id_usuario = :id", {'id': usuario_id})
        resultado_rutina_asignada = cursor.fetchone()
        rutina_asignada = resultado_rutina_asignada[0] if resultado_rutina_asignada else None
        print(f"Rutina asignada actualmente: {rutina_asignada}")

        # BLOQUE POST PARA GENERAR RUTINA
        if request.method == 'POST' and 'mensaje' not in request.POST:
            print("Recibido POST para asignar rutina")

            cursor.execute("UPDATE usuario SET id_rutina_asignada = :id_rutina WHERE id_usuario = :id_usuario",
                           {'id_rutina': id_rutina, 'id_usuario': usuario_id})
            print("Rutina asignada al usuario")

            cursor.execute("DELETE FROM rutina_ejercicios WHERE id_rutina = :id_rutina", {'id_rutina': id_rutina})
            print("Ejercicios anteriores de la rutina eliminados")

            

        if not rutina_asignada:
            print("Usuario no tiene rutina asignada aún.")
            context = {
                'mensaje': 'No tienes una rutina asignada. Puedes generarla ahora.',
                'tiene_rutina': False,
                'rutina_por_dia_lista': [],
                'chat': chat    
            }
            template = 'fitplace/Rutinas.html' if plan_id == 1 else 'fitplace/EliteFit/RutinasELITE.html'
            return render(request, template, context)

        cursor.execute("""
            SELECT re.dia_semana, e.nombre_ejercicio, e.descripcion
            FROM rutina_ejercicios re
            JOIN ejercicio e ON re.id_ejercicio = e.id_ejercicio
            WHERE re.id_rutina = :id_rutina
        """, {'id_rutina': rutina_asignada})
        resultados = cursor.fetchall()
        print("Ejercicios encontrados para la rutina asignada:")
        for row in resultados:
            print(row)

        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        rutina_por_dia = {dia: [] for dia in dias_orden}
        for dia, nombre, descripcion in resultados:
            rutina_por_dia[dia].append({'nombre': nombre, 'descripcion': descripcion})

        rutina_por_dia_lista = [(dia, rutina_por_dia[dia]) for dia in dias_orden]

        context = {
            'tiene_rutina': True,
            'nombre_rutina': nombre_rutina,
            'descripcion_rutina': descripcion_rutina,
            'mensaje': '',
            'rutina_por_dia_lista': rutina_por_dia_lista,
            'chat': chat,
            'nombre_usuario_logueado': nombre_usuario
        }
        print("Renderizando plantilla con rutina asignada y ejercicios filtrados por día.")
        template = 'fitplace/Rutinas.html' if plan_id == 1 else 'fitplace/EliteFit/RutinasELITE.html'
        return render(request, template, context)



def principal(request):
    os.system("cls")
    print("Bienvenido a principal!")
    usuario_id = request.session.get('user_id')
    if not usuario_id:
        return redirect('index')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PLAN_ID_PLAN
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :usuario_id
        """, {'usuario_id': usuario_id})
        row = cursor.fetchone()
    ##Aquí extraemos el ID_Plan que pertenece al usuario logueado
    plan_id = row[0]

    ##Aquí le decimos que si el plan_id es igual a 1 vaya a el template free y si es 2
    ##Vaya el template premium
    if plan_id == 1:
        return render(request, 'fitplace/Principal.html')
    elif plan_id == 2:
        return render(request, 'fitplace/EliteFit/PrincipalElite.html')


    return render(request,'fitplace/Principal.html')    
    
def comunidad(request):
    # Validación para el tipo de plan
    usuario_id = request.session.get('user_id')
    if not usuario_id:
        return redirect('index')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PLAN_ID_PLAN
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :usuario_id
        """, {'usuario_id': usuario_id})
        row = cursor.fetchone()
    
    plan_id = row[0] if row else None

    # Aquí rescatamos la data de la base de datos de la tabla PUBLICACION
    with connection.cursor() as cursor:
        cursor.execute("""SELECT TITULO, MENSAJE, FECHA FROM ADMIN.PUBLICACION ORDER BY FECHA DESC""")
        publicacion = cursor.fetchall()

    context = {'publicacion': publicacion}

    # Aquí enviamos con el método POST la publicación a la base de datos
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        mensaje = request.POST.get('mensaje')
        print(f"POST recibido: Titulo: {titulo}, Mensaje: {mensaje}")

        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO ADMIN.PUBLICACION (TITULO, MENSAJE, FECHA)
                VALUES (:titulo, :mensaje, SYSDATE)
            """, {'titulo': titulo, 'mensaje': mensaje})
            cursor.close()
            print("Publicación subida correctamente.")

            messages.success(request, "Publicación subida correctamente.")
            return redirect('comunidad')

        except Exception as e:
            print(f"Error al querer subir una publicacion: {e}")
            messages.error(request, f"Error al querer subir una publicacion: {e}")
            return redirect('comunidad')

    # Renderizar según el tipo de plan
    if plan_id == 1:
        return render(request, 'fitplace/Comunidad.html', context)
    elif plan_id == 2:
        return render(request, 'fitplace/EliteFit/ComunidadElite.html', context)
    else:
        messages.error(request, "No tienes un plan asociado.")
        return redirect('index')

    
def retroalimentacion(request):
    context={}
    return render(request,'fitplace/retroalimentacion.html', context)   

def nutricion(request):
    usuario_id = request.session.get('user_id')
    os.system("cls")
    print(f'Bienvenido al apartado de nutrición del usuario ID: {usuario_id}')

    # Obtener el tipo de plan del usuario
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PLAN_ID_PLAN
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :id_usuario
        """, {'id_usuario': usuario_id})
        plan_row = cursor.fetchone()
    plan_id = plan_row[0] if plan_row else 1  # Por defecto 1 (Free) si no se encuentra

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EDAD, ESTATURA, PESO, SEXO, OBJETIVO
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :id_usuario
        """, {'id_usuario': usuario_id})
        user_data = cursor.fetchone()

    if user_data:
        edad = int(user_data[0])
        estatura_metros = float(user_data[1])
        peso = float(user_data[2])
        sexo = user_data[3]
        objetivo = user_data[4] or ''

        estatura_cm = estatura_metros * 100

        # Tasa Metabólica Basal (TMB) usando Harris-Benedict
        if sexo.upper() == 'M':
            tmb = 10 * peso + 6.25 * estatura_cm - 5 * edad + 5
        else:
            tmb = 10 * peso + 6.25 * estatura_cm - 5 * edad - 161

        # Actividad moderada
        calorias_base = tmb * 1.55

        objetivo = objetivo.lower()
        ajuste_calorias = 1.0
        proteina_extra = 0

        if 'masa muscular' in objetivo:
            ajuste_calorias = 1.20
            proteina_extra = 0.5
        elif 'perdida' in objetivo or 'grasa' in objetivo:
            ajuste_calorias = 0.80
            proteina_extra = 0.5
        elif 'fuerza' in objetivo:
            ajuste_calorias = 1.15
            proteina_extra = 0.4
        elif 'flexibilidad' in objetivo:
            ajuste_calorias = 1.0
            proteina_extra = 0.2

        calorias = calorias_base * ajuste_calorias
        proteinas = peso * (2 + proteina_extra)
        grasas = peso * 1
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

    template = 'fitplace/nutricion.html' if plan_id == 1 else 'fitplace/EliteFit/nutricionELITE.html'
    return render(request, template, context)


def perfil(request):
    usuario_id = request.session.get('user_id')
    if not usuario_id:
        return redirect('index')

    try:
        with connection.cursor() as cursor:
            # Obtener datos del usuario y su plan
            cursor.execute("""
                SELECT NOMBRE_COMPLETO, CORREO_ELECTRONICO, PESO, ESTATURA, EDAD, SEXO, OBJETIVO, PLAN_ID_PLAN
                FROM ADMIN.USUARIO
                WHERE ID_USUARIO = :id_usuario
            """, {'id_usuario': usuario_id})
            row = cursor.fetchone()

        if not row:
            messages.error(request, "No se encontró el usuario.")
            return redirect('index')

        nombre, correo, peso, estatura, edad, sexo, objetivo, plan_id = row

        genero = {
            'M': 'Masculino',
            'F': 'Femenino'
        }.get(sexo.upper(), 'Otro')

        context = {
            'nombre': nombre,
            'correo': correo,
            'peso': peso,
            'estatura': estatura,
            'edad': edad,
            'genero': genero,
            'objetivo': objetivo if objetivo else 'No definido'
        }

        # Render según el tipo de plan
        if plan_id == 1:
            return render(request, 'fitplace/Perfil.html', context)
        elif plan_id == 2:
            return render(request, 'fitplace/EliteFit/PerfilELITE.html', context)
        else:
            messages.error(request, "Tipo de plan desconocido.")
            return redirect('index')

    except Exception as e:
        messages.error(request, f"Ocurrió un error al cargar el perfil: {e}")
        return redirect('index')


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
    usuario_id = request.session.get('user_id')
    print(f'ID del usuario: {usuario_id}.')
    plan_actual = None  # Valor por defecto

    if usuario_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT PLAN_ID_PLAN FROM ADMIN.USUARIO
                WHERE ID_USUARIO = :usuario_id
            """, {'usuario_id': usuario_id})
            row = cursor.fetchone()
            if row:
                plan_actual = row[0]
                print(f'Plan actual del usuario: {plan_actual}')

    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        print(f'Nuevo plan seleccionado: {plan_id}.')
        if usuario_id and plan_id:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ADMIN.USUARIO
                    SET PLAN_ID_PLAN = :plan_id
                    WHERE ID_USUARIO = :usuario_id
                """, {'plan_id': plan_id, 'usuario_id': usuario_id})
            print('Plan del usuario actualizado correctamente')
            return redirect('perfil')
        else:
            print('Error al actualizar el plan del usuario.')
            return render(request, 'fitplace/Planes.html', {
                'error': 'Debe seleccionar un plan',
                'plan_actual': plan_actual
            })

    return render(request, 'fitplace/Planes.html', {'plan_actual': plan_actual})


def pago(request):
    context={}
    return render(request,'fitplace/Pago.html', context) 