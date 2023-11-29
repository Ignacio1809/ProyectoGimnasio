from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
import re
from .models import *
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from mercadopago import SDK
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Create your views here.
def Home(request):
    plans = Plan.objects.all()
    return render(request,"index.html", {'plan':plans} )

def is_valid_gmail(email):
    """Verifica si el correo electrónico proporcionado tiene un formato de Gmail válido."""
    pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
    return re.match(pattern, email)

def handlelogin(request):
    if request.method=="POST":
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')

        if cliente.objects.filter(email=email).exists():
            usuario = cliente.objects.get(email=email)
            user = User.objects.get(email=email)
            if (pass1 == usuario.passwrd):
                messages.success(request, "Has iniciado sesión exitosamente.")
                login(request,user)
                return redirect('/')
            else:
                messages.error(request, "Credenciales Invalidas")
                return redirect('/login')
        else:
                messages.error(request, "Credenciales Invalidas")
                return redirect('/login')


    return render(request,"handlelogin.html")

def signup(request):
    if request.method == 'POST':
        number = request.POST['usernumber']
        name = request.POST['fname']
        lname = request.POST['lastname']
        email = request.POST['email']
        weight = float(request.POST['weight'])
        height = float(request.POST['height'])/100
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        imc = weight/height**2
        birth= request.POST['birthdate']
        if len(number)>9 or len(number)<9:
            messages.info(request, "El telefono ingresado debe tener al menos 9 dígitos")
            return redirect('/signup')
       
        if pass1 != pass2:
            messages.info(request, "Las contraseñas ingresadas no son iguales.")
            return redirect('/signup')
        
        # Validar fuerza de contraseña
        try:
            validate_password_strength(pass1)
        except ValidationError as e:
            messages.info(request, e.message)
            return redirect('/signup')
        
        # Verificar si el correo ya existe
        if cliente.objects.filter(email=email).exists():
            messages.info(request, "El correo electrónico ingresado ya está en uso.")
            return redirect('/signup')

        # Crear usuario de Django
        user = User.objects.create_user(username=name, email=email, password=pass1)
        usuario = cliente.objects.create(
            telefono=number, nombre=name, apellido=lname, email=email, estatura=height, peso=weight, imc=imc, fecha_nac=birth, passwrd=pass1)
        
        request.session['user_email'] = email

        messages.info(request, "Usuario creado con éxito.")
        return redirect('/login')
    
    return render(request,"signup.html")
    

def handleLogout(request):
    logout(request)
    messages.success(request, "Has cerrado tu sesión exitosamente")
    return redirect('/login')

def all_plans(request):
    # Obtener todos los planes
    plans = Plan.objects.all()
    if request.method=="GET":
        return render(request, "plans.html", {'plan': plans})
    else:
        id = request.POST['id']
        plan = Plan.objects.get(id=id)
        return render(request, "plan_detail.html", {'p': plan})
    
def single_plan(request, Plan_id):
    plan = Plan.objects.get(id=Plan_id)
    return render(request, "plan_detail.html", {'p': plan})

def validate_password_strength(value):
    if not re.search(r'[A-Z]', value): 
        raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    if not re.search(r'[a-z]', value): 
        raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
    if not re.search(r'[0-9]', value): 
        raise ValidationError('La contraseña debe contener al menos un número.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value): 
        raise ValidationError('La contraseña debe contener al menos un símbolo.')

def create_payment(request, plan_id):
    if not request.user.is_authenticated:
        # Si el usuario no está autenticado, redirígelo a la página de inicio de sesión
        messages.error(request, "Por favor, inicia sesión para continuar.")
        return redirect('login')
    
    if request.method == "POST":
        # Traer el plan seleccionado basado en plan_id
        plan = get_object_or_404(Plan, pk=plan_id)
        
        # Almacenar el plan_id en la sesión para usar después del pago
        request.session['plan_id'] = plan_id
        
        # Instanciar el SDK de Mercado Pago con el access token
        sdk = SDK("APP_USR-6900103224898204-111921-e3c875584a5866ccde9f4635e32722a4-1555939347")
        
        # Crear datos de la preferencia de pago
        preference_data = {
            "items": [
                {
                    "title": plan.nombre_plan,
                    "description": plan.descripcion,
                    "quantity": 1,
                    "currency_id": "CLP",
                    "unit_price": plan.precio
                }
            ],
            "back_urls": {
                "success": "https://wxfleh.pythonanywhere.com/payment_success/",
                "failure": "https://wxfleh.pythonanywhere.com/pago_fallido/",
            },
            # Asumiendo que quieres pasar el email del cliente como referencia externa
            "external_reference": request.user.email,
        }
        
        # Crear la preferencia de pago en Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        
        # Obtener el enlace de pago desde la respuesta
        payment_link = preference_response["response"]["init_point"]
        
        # Redirigir al usuario al enlace de pago
        return redirect(payment_link)
    
    else:
        # Si no es POST, simplemente mostramos la página con el formulario de pago
        plan = get_object_or_404(Plan, pk=plan_id)
        return render(request, "plan_detail.html", {'p': plan})
    

def payment_success(request):
    # Asumiendo que usas la autenticación de Django y que el email del usuario está en la sesión.
    if request.user.is_authenticated:
        # Obteniendo email y plan_id de la sesión en lugar de la URL para mayor seguridad.
        email_cliente = request.session.get('user_email', request.user.email)
        plan_id = request.session.get('plan_id')
        
        if not plan_id:
            messages.error(request, "No se pudo completar la compra. Falta información del plan.")
            return redirect('pago_fallido')

        try:
            cliente_obj = get_object_or_404(cliente, email=email_cliente)
            plan_obj = get_object_or_404(Plan, pk=plan_id)

            cliente_obj.plan_actual = plan_obj
            cliente_obj.save()

            # Limpiando la información de la sesión después de usarla.
            del request.session['plan_id']
            del request.session['user_email']

            messages.success(request, "Compra realizada con éxito.")
            return redirect('profile')  # Redirige a la ruta de nombre 'profile'
        except cliente.DoesNotExist:
            messages.error(request, "No se encontró el cliente.")
            return redirect('pago_fallido')
        except Plan.DoesNotExist:
            messages.error(request, "No se encontró el plan.")
            return redirect('pago_fallido')
        except Exception as e:
            # Agregar manejo de excepciones más detallado
            messages.error(request, str(e))
            return redirect('pago_fallido')
    else:
        messages.error(request, "Usuario no autenticado.")
        return redirect('login')

User = get_user_model()


@require_POST
def update_video_status(request):
    data = json.loads(request.body)
    video_id = data.get('video_id')
    viewed_status = data.get('viewed')

    VideoView.objects.update_or_create(
        user=request.user,
        video_id=video_id,
        defaults={'viewed': viewed_status}
    )

    videos_vistos = VideoView.objects.filter(user=request.user, viewed=True).count()
    total_videos = Video.objects.count()
    progress_percent = (videos_vistos / total_videos) * 100 if total_videos else 0

    return JsonResponse({'success': True, 'progress_percent': progress_percent})

def profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('handlelogin')

    try:
        cliente_obj = cliente.objects.get(email=user.email)
        plan_actual = cliente_obj.plan_actual
        videos_vistos_ids = VideoView.objects.filter(user=user, viewed=True).values_list('video_id', flat=True)
        total_videos = Video.objects.count()  # O la cantidad de videos en el plan actual
        progress_percent = (len(videos_vistos_ids) / total_videos) * 100 if total_videos > 0 else 0

        context = {
            'cliente': cliente_obj,
            'plan': plan_actual,
            'videos_vistos_ids': list(videos_vistos_ids),
            'progress_percent': progress_percent,
        }
        return render(request, "profile.html", context)
    except cliente.DoesNotExist:
        return render(request, "error.html", {'mensaje': "Perfil no encontrado."})




def pago_fallido(request):
    return render(request, "pago_fallido.html")

def home(request):
    return render(request, 'index.html')

