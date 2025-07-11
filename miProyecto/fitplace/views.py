import random
import smtplib
import ssl
import unicodedata
import time
import os
import json

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
from datetime import datetime


from django.contrib import messages
from django.contrib.auth.decorators import login_required



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
            return redirect('cambiarcredencialescode')
        else:
            messages.error(request, "Código incorrecto.")
            mostrar_modal = True

    return render(request, 'fitplace/RecuperarPass.html', {'mostrar_modal': mostrar_modal})

def cambiarcredencialescode(request):
    context={}
    return render(request,'fitplace/cambiarcredencialescode.html', context) 


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
        elif not correo: # Cambio aquí: Si correo es None o vacío, maneja el error.
            messages.error(request, "No se encontró un correo válido para restablecer la contraseña. Por favor, reinicia el proceso de recuperación.")
            # Puedes redirigir a recuperarpass o login aquí
            return redirect('recuperarpass') # O 'login'
        else: # Si correo existe y las contraseñas coinciden
            try:
                # No es estrictamente necesario el str() cast aquí si ya validamos que no es None,
                # pero no hace daño para asegurar que cx_Oracle reciba un string.
                nueva_pass_str = str(nueva_pass)
                correo_str = str(correo)

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
                        messages.error(request, "No se encontró usuario con ese correo o la contraseña es la misma.")
                    else:
                        print("Contraseña actualizada con éxito, redirigiendo...")
                        messages.success(request, "Contraseña actualizada correctamente.")
                        # Limpia la sesión para evitar reusar el token de recuperación
                        request.session.pop('correo_recuperacion', None)
                        request.session.pop('codigo_recuperacion', None)
                        return render(request, 'fitplace/RestablecerPass.html', {'success_alert': True}) # Pasa una bandera para activar SweetAlert2
            except Exception as e:
                # El error parece ocurrir en esta línea de impresión o en alguna otra interna del cursor
                # Mantendremos la impresión para depuración, pero se debe revisar el stack trace completo
                print(f"Exception al actualizar contraseña: {e}")
                messages.error(request, f"Error al actualizar contraseña: {e}. Si el problema persiste, contacta a soporte.")
    
    # Renderiza la plantilla con el contexto de errores si los hay, o sin ellos si es GET.
    # Si viene de un POST exitoso, 'success_alert' será True y activará el JS.
    return render(request, 'fitplace/RestablecerPass.html', {'success_alert': False})



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

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PLAN_ID_PLAN
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :usuario_id
        """, {'usuario_id': usuario_id})
        row = cursor.fetchone()
    plan_id = row[0] if row else None

    id_entrenador = 700000

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

    with connection.cursor() as cursor:
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
            template = 'fitplace/Rutinas.html' if plan_id == 1 else 'fitplace/EliteFit/RutinasELITE.html'
            return render(request, template, context)

        cursor.execute("SELECT id_rutina, nombre_rutina, descripcion FROM rutina WHERE objetivo = :obj", {'obj': objetivo})
        rutina = cursor.fetchone()
        print(f"Rutina encontrada para el objetivo: {rutina}")

        if not rutina:
            context = {
                'mensaje': f'No existe una rutina disponible para el objetivo "{objetivo}".',
                'tiene_rutina': False,
                'rutina_por_dia_lista': [],
                'chat': chat
            }
            template = 'fitplace/Rutinas.html' if plan_id == 1 else 'fitplace/EliteFit/RutinasELITE.html'
            return render(request, template, context)

        id_rutina, nombre_rutina, descripcion_rutina = rutina

        cursor.execute("SELECT id_rutina_asignada FROM usuario WHERE id_usuario = :id", {'id': usuario_id})
        resultado_rutina_asignada = cursor.fetchone()
        rutina_asignada = resultado_rutina_asignada[0] if resultado_rutina_asignada else None
        print(f"Rutina asignada actualmente: {rutina_asignada}")

        if request.method == 'POST' and 'mensaje' not in request.POST:
            print("Recibido POST para asignar rutina")

            cursor.execute("UPDATE usuario SET id_rutina_asignada = :id_rutina WHERE id_usuario = :id_usuario",
                           {'id_rutina': id_rutina, 'id_usuario': usuario_id})
            print("Rutina asignada al usuario")

            cursor.execute("DELETE FROM rutina_ejercicios WHERE id_rutina = :id_rutina", {'id_rutina': id_rutina})
            print("Ejercicios anteriores de la rutina eliminados")

        if not rutina_asignada:
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

        # Definir valores en duro según objetivo
        # Valores base
        series, repeticiones = 3, '12'
        peso = 'Peso moderado'
        descanso = '60 segundos'  # valor base

        # Ajustes según objetivo
        if objetivo == 'masa muscular':
            series = 4
            repeticiones = '10'
            descanso = '90 segundos'
        elif objetivo == 'fuerza':
            series = 5
            repeticiones = '5'
            descanso = '120 segundos'  # antes era 10 minutos, ahora 2 minutos
            peso = 'Peso alto'
        elif objetivo == 'perdida grasa':
            series = 3
            repeticiones = '18'
            descanso = '30 segundos'
            peso = 'Peso bajo'
        elif objetivo == 'flexibilidad':
            series = 3
            repeticiones = '45 segundos'
            descanso = '15 segundos'
            peso = 'Sin peso'

        for dia, nombre, descripcion in resultados:
            rutina_por_dia[dia].append({
                'nombre': nombre,
                'descripcion': descripcion,
                'series': series,
                'repeticiones': repeticiones,
                'peso': peso,
                'descanso': descanso
            })

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
        template = 'fitplace/Rutinas.html' if plan_id == 1 else 'fitplace/EliteFit/RutinasELITE.html'
        return render(request, template, context)


def enviar_mensaje_chat_cliente_post(request):
    usuario_id = request.session.get('user_id')
    print(f"enviar_mensaje_chat_cliente_post: Usuario ID {usuario_id} intentando enviar mensaje.")

    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para enviar mensajes.")
        return redirect('login') # O a la página de rutinas si lo prefieres

    mensaje_texto = request.POST.get('mensaje_chat') # Asegúrate que el name del input en el HTML sea 'mensaje_chat'
    id_entrenador = 700000 # Asumimos que el cliente siempre chatea con el entrenador principal

    if not mensaje_texto or not mensaje_texto.strip():
        messages.error(request, "El mensaje no puede estar vacío.")
        return redirect('rutinas') # Redirige a la página de rutinas del cliente

    try:
        with connection.cursor() as cursor:
            # Obtener nombre del usuario emisor
            cursor.execute("SELECT nombre_completo FROM usuario WHERE id_usuario = :id", {'id': usuario_id})
            resultado_emisor = cursor.fetchone()
            nombre_emisor = str(resultado_emisor[0]) if resultado_emisor else "Cliente Desconocido"

            print(f"Preparando inserción: Emisor={usuario_id}, Receptor={id_entrenador}, Nombre={nombre_emisor}, Mensaje='{mensaje_texto}'")

            cursor.execute("""
                INSERT INTO CHAT_PERSONAL_TRAINER (ID_EMISOR, ID_RECEPTOR, NOMBRE_EMISOR, MENSAJE, FECHA)
                VALUES (:id_emisor, :id_receptor, :nombre_emisor, :mensaje, SYSDATE)
            """, {
                'id_emisor': usuario_id,
                'id_receptor': id_entrenador,
                'nombre_emisor': nombre_emisor,
                'mensaje': mensaje_texto.strip()
            })
            connection.commit() # Asegurarse de hacer commit
            print("Mensaje insertado exitosamente.")
            messages.success(request, "Mensaje enviado correctamente.")
    except Exception as e:
        print(f"Error CRÍTICO al enviar mensaje desde cliente (enviar_mensaje_chat_cliente_post): {e}")
        messages.error(request, f"Error al enviar mensaje: {e}. Por favor, inténtalo de nuevo.")
        # Aquí es donde el error de la "llave" debería aparecer. Puedes poner un breakpoint aquí.

    return redirect('rutinas') # Redirige a la página de rutinas del cliente después de enviar el mensaje


@require_POST
@csrf_exempt # ¡MANTÉN ESTO SOLO PARA DEPURACIÓN! Elimínalo en producción.
def enviar_mensaje_chat(request):
    print("\n--- INICIO DEPURACIÓN: enviar_mensaje_chat ---")
    
    usuario_id = request.session.get('user_id')
    print(f"DEBUG: 1. Usuario ID de sesión: {usuario_id}")

    if not usuario_id:
        print("DEBUG: 1.1. Usuario no autenticado. Retornando JsonResponse.")
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)

    mensaje_texto = request.POST.get('mensaje')
    print(f"DEBUG: 2. Mensaje recibido: '{mensaje_texto}'")

    receptor_id_str = request.POST.get('receptor_id')
    print(f"DEBUG: 3. ID de Receptor (string): '{receptor_id_str}'")

    # --- LÓGICA DE CORRECCIÓN PARA ID_RECEPTOR ---
    id_entrenador_principal = 700000 # Definimos el ID del entrenador principal

    if not receptor_id_str or receptor_id_str == '-1': # Si es vacío o "-1", asumimos que es el cliente enviando al entrenador principal
        id_receptor = id_entrenador_principal
        print(f"DEBUG: 3.1. receptor_id no proporcionado o es '-1'. Asumiendo ID_RECEPTOR = {id_receptor} (Entrenador Principal).")
    else:
        try:
            id_receptor = int(receptor_id_str)
            print(f"DEBUG: 3.2. ID de Receptor (int): {id_receptor}")
        except (ValueError, TypeError) as e:
            print(f"ERROR: 3.3. ID de receptor inválido o no numérico: {receptor_id_str}. Error: {e}")
            return JsonResponse({'success': False, 'error': 'ID de receptor inválido o no numérico'}, status=400)
    # --- FIN LÓGICA DE CORRECCIÓN ---

    if not mensaje_texto or not mensaje_texto.strip():
        print("DEBUG: 4. Mensaje vacío. Retornando JsonResponse.")
        return JsonResponse({'success': False, 'error': 'Mensaje vacío'}, status=400)

    try:
        with connection.cursor() as cursor:
            print("DEBUG: 5. Conexión a la base de datos establecida.")
            cursor.execute("SELECT nombre_completo FROM usuario WHERE id_usuario = :id", {'id': usuario_id})
            resultado_emisor = cursor.fetchone()
            
            if not resultado_emisor:
                print(f"ERROR: 5.1. Nombre de emisor no encontrado para ID: {usuario_id}. Retornando JsonResponse.")
                return JsonResponse({'success': False, 'error': 'Nombre de emisor no encontrado'}, status=400)
            
            nombre_emisor = str(resultado_emisor[0])
            print(f"DEBUG: 5.2. Nombre del emisor obtenido: '{nombre_emisor}'")

            print("DEBUG: 6. Preparando para ejecutar INSERT en CHAT_PERSONAL_TRAINER...")
            print(f"   Valores FINALES: ID_EMISOR={usuario_id}, ID_RECEPTOR={id_receptor}, NOMBRE_EMISOR='{nombre_emisor}', MENSAJE='{mensaje_texto.strip()}'")

            cursor.execute("""
                INSERT INTO CHAT_PERSONAL_TRAINER (ID_EMISOR, ID_RECEPTOR, NOMBRE_EMISOR, MENSAJE, FECHA)
                VALUES (:id_emisor, :id_receptor, :nombre_emisor, :mensaje, SYSDATE)
            """, {
                'id_emisor': usuario_id,
                'id_receptor': id_receptor,
                'nombre_emisor': nombre_emisor,
                'mensaje': mensaje_texto.strip()
            })
            
            print("DEBUG: 7. Sentencia INSERT ejecutada. Intentando COMMIT...")
            connection.commit() 
            print("DEBUG: 8. COMMIT de la transacción exitoso.")
            
        print("DEBUG: 9. Mensaje enviado exitosamente. Retornando JsonResponse éxito.")
        return JsonResponse({'success': True, 'mensaje_enviado': mensaje_texto, 'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M")})
    
    except Exception as e:
        print(f"ERROR CRÍTICO: 10. Excepción inesperada en enviar_mensaje_chat: {e}")
        try:
            connection.rollback()
            print("DEBUG: 10.1. ROLLBACK ejecutado debido a una excepción.")
        except Exception as rb_e:
            print(f"DEBUG: 10.2. Error durante el rollback: {rb_e}")
        
        print("DEBUG: 10.3. Retornando JsonResponse con error.")
        return JsonResponse({'success': False, 'error': f"Error al enviar mensaje: {str(e)}"}, status=500)

    finally:
        print("--- FIN DEPURACIÓN: enviar_mensaje_chat ---\n")
# Agrega una nueva vista para cargar mensajes via AJAX
def cargar_mensajes_chat(request, cliente_id=None):
    usuario_logueado_id = request.session.get('user_id')

    if not usuario_logueado_id:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)

    # Lógica para determinar el emisor y el receptor para la consulta del chat
    if cliente_id: # La solicitud es del entrenador, cliente_id es el cliente con quien chatea
        id_entrenador = usuario_logueado_id
        id_cliente_para_chat = cliente_id
        id_para_comparacion_es_mio = id_entrenador
    else: # La solicitud es del cliente (desde RutinasELITE.html)
        id_cliente_para_chat = usuario_logueado_id
        id_entrenador = 700000 # O el ID del entrenador asignado a este cliente si lo obtienes dinámicamente
        id_para_comparacion_es_mio = id_cliente_para_chat

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ID_CHAT, MENSAJE, FECHA, NOMBRE_EMISOR, ID_EMISOR, ID_RECEPTOR
                FROM CHAT_PERSONAL_TRAINER
                WHERE (ID_EMISOR = :id_cliente AND ID_RECEPTOR = :id_entrenador)
                OR (ID_EMISOR = :id_entrenador AND ID_RECEPTOR = :id_cliente)
                ORDER BY FECHA ASC
            """, {'id_cliente': id_cliente_para_chat, 'id_entrenador': id_entrenador})

            chat_data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            messages_list = []
            for row in chat_data:
                msg_dict = dict(zip(columns, row))

                # Manejo específico para columnas LOB si existen
                for key, value in msg_dict.items():
                    # Si el valor es un objeto LOB (ej. cx_Oracle.LOB), léelo
                    if hasattr(value, 'read'): # Una forma de verificar si es un objeto LOB
                        msg_dict[key] = value.read() # Lee el contenido del LOB
                        if isinstance(msg_dict[key], bytes): # Si es bytes, decodifica a string
                            msg_dict[key] = msg_dict[key].decode('utf-8') # Ajusta la codificación si es diferente

                # Formatear la fecha para que JavaScript la reciba legible
                if 'FECHA' in msg_dict and isinstance(msg_dict['FECHA'], datetime):
                    msg_dict['FECHA'] = msg_dict['FECHA'].strftime("%d-%m-%Y %H:%M")

                # Lógica para determinar si el mensaje fue enviado por el usuario logueado actualmente
                msg_dict['ES_MIO'] = (msg_dict['ID_EMISOR'] == id_para_comparacion_es_mio)

                messages_list.append(msg_dict)

        return JsonResponse({'success': True, 'chat': messages_list})

    except Exception as e:
        print(f"Error al cargar mensajes de chat: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



# Función auxiliar para verificar si el usuario logueado es un entrenador
def es_entrenador(user_id_from_session):
    if not user_id_from_session:
        return False
    try:
        with connection.cursor() as cursor:
            # Asume que el usuario de la sesión se corresponde con un ID_USUARIO en tu tabla USUARIO
            cursor.execute("SELECT ROL_ID_ROL FROM USUARIO WHERE ID_USUARIO = :id", {'id': user_id_from_session})
            rol_id = cursor.fetchone()
            # Verifica si el ROL_ID_ROL es 3 (Entrenador)
            return rol_id and rol_id[0] == 3
    except Exception as e:
        print(f"Error al verificar rol de usuario {user_id_from_session}: {e}")
        return False

# Decorador personalizado para usar con el ID de sesión
def entrenador_required(function):
    def wrap(request, *args, **kwargs):
        if not es_entrenador(request.session.get('user_id')):
            messages.warning(request, "No tienes permisos para acceder a esta sección.")
            return redirect('login') # Redirige a login o a una página de error
        return function(request, *args, **kwargs)
    return wrap

# Vista para el panel de chats del entrenador
@entrenador_required
def panel_entrenador_chats(request):
    entrenador_id = request.session.get('user_id')
    print(f"ID del entrenador logueado: {entrenador_id}")
    chats_clientes = []
    try:
        with connection.cursor() as cursor:
            # Esta consulta obtiene a los clientes que han enviado/recibido mensajes del entrenador
            cursor.execute("""
                SELECT DISTINCT
                    CASE
                        WHEN C.ID_EMISOR = :entrenador_id THEN C.ID_RECEPTOR
                        ELSE C.ID_EMISOR
                    END AS ID_USUARIO_CLIENTE,
                    (SELECT U.NOMBRE_COMPLETO FROM USUARIO U WHERE U.ID_USUARIO = (
                        CASE
                            WHEN C.ID_EMISOR = :entrenador_id THEN C.ID_RECEPTOR
                            ELSE C.ID_EMISOR
                        END
                    )) AS NOMBRE_CLIENTE
                FROM CHAT_PERSONAL_TRAINER C
                WHERE C.ID_EMISOR = :entrenador_id OR C.ID_RECEPTOR = :entrenador_id
                ORDER BY NOMBRE_CLIENTE ASC
            """, {'entrenador_id': entrenador_id})
            
            for row in cursor.fetchall():
                cliente_id = row[0]
                cliente_nombre = str(row[1]) if row[1] else "Cliente Desconocido"
                chats_clientes.append({'id': cliente_id, 'nombre': cliente_nombre})

    except Exception as e:
        print(f"Error al cargar lista de chats para entrenador: {e}")
        messages.error(request, f"Error al cargar la lista de chats: {e}")

    context = {
        'chats_clientes': chats_clientes
    }
    # Asegúrate de que este nombre coincida con tu HTML
    return render(request, 'fitplace/PanelEntrenador.html', context) # <--- ¡Aquí usas 'PanelEntrenador.html'!


# Vista para el chat individual del entrenador con un usuario
@entrenador_required
def chat_entrenador_usuario(request, cliente_id): # El ID del cliente con el que el entrenador chateará
    entrenador_id = request.session.get('user_id')
    
    # Lógica para enviar mensaje del entrenador al usuario (POST)
    if request.method == 'POST':
        mensaje_texto = request.POST.get('mensaje')
        if not mensaje_texto or not mensaje_texto.strip():
            return JsonResponse({'success': False, 'error': 'Mensaje vacío'}, status=400)

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT NOMBRE_COMPLETO FROM USUARIO WHERE ID_USUARIO = :id", {'id': entrenador_id})
                nombre_entrenador_raw = cursor.fetchone()
                nombre_entrenador = str(nombre_entrenador_raw[0]) if nombre_entrenador_raw else "Entrenador Desconocido"

                cursor.execute("""
                    INSERT INTO CHAT_PERSONAL_TRAINER (ID_EMISOR, ID_RECEPTOR, NOMBRE_EMISOR, MENSAJE, FECHA)
                    VALUES (:id_emisor, :id_receptor, :nombre_emisor, :mensaje, SYSDATE)
                """, {
                    'id_emisor': entrenador_id,
                    'id_receptor': cliente_id,
                    'nombre_emisor': nombre_entrenador,
                    'mensaje': mensaje_texto.strip()
                })
            return JsonResponse({'success': True, 'mensaje_enviado': mensaje_texto, 'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M")})
        except Exception as e:
            print(f"Error al enviar mensaje como entrenador: {e}")
            return JsonResponse({'success': False, 'error': f"Error al enviar mensaje: {e}"}, status=500)

    # Lógica para cargar mensajes (GET)
    chat_data = []
    nombre_cliente = "Cliente Desconocido"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOMBRE_COMPLETO FROM USUARIO WHERE ID_USUARIO = :id", {'id': cliente_id})
            nombre_cliente_raw = cursor.fetchone()
            if nombre_cliente_raw:
                nombre_cliente = str(nombre_cliente_raw[0])

            cursor.execute("""
                SELECT MENSAJE, FECHA, NOMBRE_EMISOR, ID_EMISOR
                FROM CHAT_PERSONAL_TRAINER
                WHERE (ID_EMISOR = :entrenador_id AND ID_RECEPTOR = :cliente_id)
                OR (ID_EMISOR = :cliente_id AND ID_RECEPTOR = :entrenador_id)
                ORDER BY FECHA ASC
            """, {'entrenador_id': entrenador_id, 'cliente_id': cliente_id})
            raw_messages = cursor.fetchall()

            for msg in raw_messages:
                chat_data.append({
                    'MENSAJE': str(msg[0]),
                    'FECHA': msg[1].strftime("%d-%m-%Y %H:%M"),
                    'NOMBRE_EMISOR': str(msg[2]),
                    'ES_MIO': msg[3] == entrenador_id # Para el entrenador, su mensaje es 'mio'
                })
    except Exception as e:
        print(f"Error al cargar chat para entrenador: {e}")
        messages.error(request, f"Error al cargar el chat con {nombre_cliente}.")

    context = {
        'chat': chat_data,
        'nombre_usuario_actual': nombre_cliente, # Nombre del cliente con el que se está chateando
        'entrenador_id': entrenador_id, # ID del entrenador logueado
        'cliente_id': cliente_id # ID del cliente actual para enviar mensajes
    }
    # Asegúrate de que este nombre coincida con tu HTML
    return render(request, 'fitplace/chat_entrenador_usuario.html', context)


def principal(request):
    os.system("cls")
    print("Bienvenido a principal!")
    usuario_id = request.session.get('user_id')
    if not usuario_id:
        return redirect('index')

    # --- INICIO: Lógica para determinar si el usuario es un entrenador ---
    es_usuario_entrenador = False
    try:
        # Asegúrate de que la función es_entrenador esté definida en este archivo
        es_usuario_entrenador = es_entrenador(usuario_id)
    except NameError:
        print("Error: La función 'es_entrenador' no está definida. Asegúrate de incluirla en views.py.")
    # --- FIN: Lógica para determinar si el usuario es un entrenador ---

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PLAN_ID_PLAN
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :usuario_id
        """, {'usuario_id': usuario_id})
        row = cursor.fetchone()
    
    plan_id = row[0]

    # Prepara el contexto para la plantilla
    context = {
        'es_entrenador': es_usuario_entrenador,
        # Puedes añadir otros datos al contexto si es necesario para principal.html o PrincipalElite.html
    }

    if plan_id == 1:
        return render(request, 'fitplace/Principal.html', context) # Pasa el contexto
    elif plan_id == 2:
        return render(request, 'fitplace/EliteFit/PrincipalElite.html', context) # Pasa el contexto

    # Esta línea se ejecutará si plan_id no es 1 ni 2, o como fallback.
    # Asegúrate de que siempre se pase el contexto.
    return render(request, 'fitplace/Principal.html', context)
    
def comunidad(request):
    usuario_id = request.session.get('user_id')
    if not usuario_id:
        return redirect('index')

    # Obtener tipo de plan
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PLAN_ID_PLAN
            FROM ADMIN.USUARIO
            WHERE ID_USUARIO = :usuario_id
        """, {'usuario_id': usuario_id})
        row = cursor.fetchone()
    plan_id = row[0] if row else None

    # Insertar nueva publicación
    if request.method == "POST" and 'titulo' in request.POST:
        titulo = request.POST.get('titulo')
        mensaje = request.POST.get('mensaje')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ADMIN.PUBLICACION (TITULO, MENSAJE, FECHA, ID_USUARIO, LIKES)
                    VALUES (:titulo, :mensaje, SYSDATE, :usuario_id, 0)
                """, {
                    'titulo': titulo,
                    'mensaje': mensaje,
                    'usuario_id': usuario_id
                })
            messages.success(request, "Publicación subida correctamente.")
            return redirect('comunidad')
        except Exception as e:
            messages.error(request, f"Error al subir publicación: {e}")
            return redirect('comunidad')

    # Obtener publicaciones y likes
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT P.TITULO, P.MENSAJE, P.FECHA, NVL(U.NOMBRE_COMPLETO, 'Anónimo'), P.LIKES, P.ID_PUBLICACION
            FROM ADMIN.PUBLICACION P
            LEFT JOIN ADMIN.USUARIO U ON U.ID_USUARIO = P.ID_USUARIO
            ORDER BY P.FECHA DESC
        """)
        publicaciones = cursor.fetchall()

    # 🔽 Aquí va tu bloque para traer los likes del usuario actual
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ID_PUBLICACION FROM LIKE_PUBLICACION
            WHERE ID_USUARIO = :usuario
        """, {'usuario': usuario_id})
        likes_usuario = {row[0] for row in cursor.fetchall()}  # Set de publicaciones likeadas

    # Enviar todo al HTML
    context = {
        'publicacion': publicaciones,
        'likes_usuario': likes_usuario
    }

    if plan_id == 2:
        return render(request, 'fitplace/EliteFit/ComunidadElite.html', context)
    else:
        return render(request, 'fitplace/Comunidad.html', context)
    
    # Vista para manejar "likes"
@require_POST
def toggle_like(request):
    id_publicacion = request.POST.get('id_publicacion')
    id_usuario = request.session.get('user_id')

    if not id_usuario:
        messages.error(request, "Debes iniciar sesión para dar like.")
        return redirect('login')

    try:
        with connection.cursor() as cursor:
            # Verificar si ya dio like antes
            cursor.execute("""
                SELECT 1 FROM LIKE_PUBLICACION
                WHERE ID_USUARIO = :usuario AND ID_PUBLICACION = :publicacion
            """, {'usuario': id_usuario, 'publicacion': id_publicacion})
            ya_dio_like = cursor.fetchone()

            if ya_dio_like:
                # 🔴 Si ya dio like, lo eliminamos y restamos
                cursor.execute("""
                    DELETE FROM LIKE_PUBLICACION
                    WHERE ID_USUARIO = :usuario AND ID_PUBLICACION = :publicacion
                """, {'usuario': id_usuario, 'publicacion': id_publicacion})

                cursor.execute("""
                    UPDATE PUBLICACION
                    SET LIKES = LIKES - 1
                    WHERE ID_PUBLICACION = :id AND LIKES > 0
                """, {'id': id_publicacion})

                messages.info(request, "Like eliminado.")
            else:
                # 🟢 Si no dio like, lo insertamos y sumamos
                cursor.execute("""
                    INSERT INTO LIKE_PUBLICACION (ID_USUARIO, ID_PUBLICACION)
                    VALUES (:usuario, :publicacion)
                """, {'usuario': id_usuario, 'publicacion': id_publicacion})

                cursor.execute("""
                    UPDATE PUBLICACION
                    SET LIKES = NVL(LIKES, 0) + 1
                    WHERE ID_PUBLICACION = :id
                """, {'id': id_publicacion})

                messages.success(request, "¡Like agregado!")

        return redirect('comunidad')

    except Exception as e:
        messages.error(request, f"Error al procesar el like: {e}")
        return redirect('comunidad')

    
def retroalimentacion(request):
    user_id = request.user.id  # ID del usuario logueado
    context = {}

    if request.method == 'POST':
        intensidad = int(request.POST.get('intensidad'))

        # Lógica para reducir series según la intensidad
        if intensidad >= 9:
            porcentaje = 0.5
        elif intensidad >= 7:
            porcentaje = 0.7
        elif intensidad >= 5:
            porcentaje = 0.85
        else:
            porcentaje = 1.0

        with connection.cursor() as cursor:
            # Consulta para obtener la cantidad total de series del usuario
            cursor.execute("""
                SELECT COUNT(*) FROM RUTINA_GENERADA
                WHERE ID_USUARIO = %s
            """, [user_id])
            total_series = cursor.fetchone()[0]

            # Cálculo de las nuevas series
            nuevas_series = round(total_series * porcentaje)

        context['total_series'] = total_series
        context['nuevas_series'] = nuevas_series
        context['intensidad'] = intensidad

    return render(request, 'fitplace/retroalimentacion.html', context)

@csrf_exempt
def guardar_retroalimentacion(request):
    if request.method == 'POST':
        intensidad = int(request.POST.get('intensidad'))
        usuario_id = request.session.get('usuario_id')  # Asumimos que el usuario está autenticado

        if not usuario_id:
            return redirect('retroalimentacion')

        # Definir el porcentaje de ajuste
        if intensidad <= 3:
            ajuste = 1.2  # Aumentar series un 20%
        elif intensidad >= 8:
            ajuste = 0.8  # Disminuir series un 20%
        else:
            ajuste = 1.0  # No modificar

        with connection.cursor() as cursor:
            # Actualiza las series por día de la rutina del usuario
            cursor.execute("""
                UPDATE RUTINA_GENERADA
                SET SERIES = ROUND(SERIES * :ajuste)
                WHERE ID_USUARIO = :usuario_id
            """, {'ajuste': ajuste, 'usuario_id': usuario_id})

        return redirect('rutinas')

    return redirect('retroalimentacion')

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
    else:
        # Si no hay usuario logueado, redirigir a login o mostrar un error
        messages.error(request, "Debes iniciar sesión para seleccionar un plan.")
        return redirect('login') # O la URL que consideres apropiada para no logueados

    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        
        # Convertir plan_id a int para comparación numérica
        try:
            plan_id = int(plan_id)
        except (ValueError, TypeError):
            messages.error(request, "Selección de plan inválida.")
            return render(request, 'fitplace/Planes.html', {'plan_actual': plan_actual})

        print(f'Nuevo plan seleccionado: {plan_id}.')

        if usuario_id and plan_id:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ADMIN.USUARIO
                    SET PLAN_ID_PLAN = :plan_id
                    WHERE ID_USUARIO = :usuario_id
                """, {'plan_id': plan_id, 'usuario_id': usuario_id})
                connection.commit() # Asegúrate de hacer commit si no usas @transaction.atomic
            
            print(f'Plan del usuario {usuario_id} actualizado a {plan_id} correctamente.')

            # --- Lógica de redirección basada en el plan seleccionado ---
            if plan_id == 2:  # Elite Fit
                print("Redirigiendo a la página de pago para ELITE FIT.")
                messages.info(request, "Has seleccionado el plan Elite Fit. Por favor, completa tu pago.")
                return redirect('pago')
            elif plan_id == 1: # Starter Fit
                print("Redirigiendo a perfil/rutinas para STARTER FIT (no requiere pago).")
                messages.success(request, "Has seleccionado el plan Starter Fit.")
                return redirect('perfil') # O 'rutinas', según tu flujo
            else:
                messages.warning(request, "Plan seleccionado no reconocido. Redirigiendo a perfil.")
                return redirect('perfil')

        else: # Este else se ejecuta si usuario_id o plan_id son None/vacío
            print('Error: Usuario ID o Plan ID faltante al intentar actualizar el plan.')
            messages.error(request, 'Debe seleccionar un plan y estar logueado.')
            return render(request, 'fitplace/Planes.html', {
                'error': 'Debe seleccionar un plan',
                'plan_actual': plan_actual
            })

    # Para solicitudes GET:
    print('Renderizando página de planes (GET request).')
    return render(request, 'fitplace/Planes.html', {'plan_actual': plan_actual})


def pago(request):
    context={}
    return render(request,'fitplace/Pago.html', context) 