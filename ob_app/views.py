from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render, get_object_or_404, render_to_response
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import EmailMessage
from django.views.generic import *
from ob_app.forms import *
from ob_app.models import *
import datetime
import random
import hashlib


def groups():
    nombres_grupo = ["Administrador", "Clientes"]

    for group in nombres_grupo:
        if Group.objects.filter(name=group).count() == 0:
            Group.objects.create(name=group)


def conv_coord(coor):
    if coor[1] == '1':
        i = 0
    elif coor[1] == '2':
        i = 6
    elif coor[1] == '3':
        i = 12
    elif coor[1] == '4':
        i = 18
    else:
        i = 24

    if coor[0] == 'A':
        pass
    elif coor[0] == 'B':
        i = i + 1
    elif coor[0] == 'C':
        i = i + 2
    elif coor[0] == 'D':
        i = i + 3
    elif coor[0] == 'E':
        i = i + 4
    else:
        i = i + 5

    return i


def get_user(user):
    if user.is_staff:
        return "{% url 'inicio' user.pk %}"
    else:
        return "{% url 'inicio' user.pk %}"


@ensure_csrf_cookie
def validate_user(request):
    groups()
    ci = request.GET.get('ci', None)
    data = {
        'user_exists': Customer.objects.filter(ident=ci).exists()
    }

    if data['user_exists']:
        data['error'] = "Usted ya se encuentra registrado. Si olvidó su clave " \
                        "ingrese a Olvidé mi contraseña"

    return JsonResponse(data)


@ensure_csrf_cookie
def first_login(request):
    customer = request.GET.get('customer', None)
    data = {
        'user_exists': Customer.objects.filter(ref=customer).exists()
    }

    if data['user_exists']:
        customer = Customer.objects.get(ref=customer)
        if customer.lastLogin is None:
            data['login'] = True
        else:
            data['login'] = False

    return JsonResponse(data)


@ensure_csrf_cookie
def validate_user_forgot(request):
    groups()
    ci = request.GET.get('ci', None)
    data = {
        'user_exists': Customer.objects.filter(ident=ci).exists()
    }

    if data['user_exists']:

        customer = Customer.objects.get(ident=ci)
        user = User.objects.get(id=customer.user.id)
        userprofile = UserProfile.objects.get(user=user)

        data['active'] = user.is_active
        data['block'] = userprofile.intent == 3

        if data['block']:
            data['error'] =  "Su cuenta se encuentra bloqueada. Comuniquese con " \
                             "atención al cliente para iniciar el proceso de desbloqueo."
            return JsonResponse(data)
        elif not (data['active']):
            data['error'] = "Su cuenta no esta activa, ingrese a su correo " \
                            "y siga los pasos para activarla para así poder reestablecer " \
                            "su contraseña"
            return JsonResponse(data)
        else:
            quest1 = customer.elemSecurity.question1
            quest2 = customer.elemSecurity.question2

            num = random.randint(1, 2)
            if num == 1:
                data['quest'] = quest1
            else:
                data['quest'] = quest2

    return JsonResponse(data)


@ensure_csrf_cookie
def validate_email(request):
    email = request.GET.get('email', None)
    first_name = request.GET.get('first_name', None)
    last_name = request.GET.get('last_name', None)
    ci = request.GET.get('ci', None)
    username = request.GET.get('username', None)

    data = {
        'user_exists': Customer.objects.filter(ident=ci).exists()
    }

    if not (data['user_exists']):
        if User.objects.filter(username=username).count() > 0:
            user = User.objects.get(username=username)
            user.delete()

        user = User(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username)
        user.is_active = False
        group = Group.objects.get(name="Clientes")
        try:
            activation_key = create_token(6)
            while UserProfile.objects.filter(activationKey=activation_key).count() > 0:
                activation_key = create_token(6)
            # mypath = os.getcwd()
            # path = Path('/Online_Banking/static/img/logo.png')
            # path = mypath + path
            # print(path)
            # file = open(path, "rb")
            # attach_image = MIMEImage(file.read())
            # attach_image.add_header('Content-Disposition', 'attachment; filename = "logo.png"')
            # msg.attach(attach_image)
            c = {'usuario': user.get_full_name,
                 'key': activation_key}
            subject = 'Actio Capital - Confirmación de Email'
            message_template = 'confirm-email.html'
            email = user.email
            send_email(subject, message_template, c, email)
            data['envio'] = True
        except:
            data['envio'] = False
            return JsonResponse(data)

        user.save()
        user.groups.add(group)
        key_expires = datetime.datetime.today() + datetime.timedelta(minutes=2)
        user_profile = UserProfile(user=user,
                                   activationKey=activation_key,
                                   keyExpires=key_expires)
        user_profile.save()

    return JsonResponse(data)


@ensure_csrf_cookie
def validate_cod(request):
    username = request.GET.get('username', None)
    token = request.GET.get('cod', None)

    data = {
        'user_exists': User.objects.filter(username=username).exists()
    }

    if data['user_exists']:
        user = User.objects.get(username=username)

        try:
            user_profile = UserProfile.objects.get(user=user, activationKey=token)
        except UserProfile.DoesNotExist:
            data['correct'] = False
            data['error'] = 'El código que ingresó es incorrecto.'
            return JsonResponse(data)

        time = datetime.datetime.today()

        if user_profile.keyExpires < time:
            data['profile_expires'] = True
            data['correct'] = False
        else:
            data['correct'] = True

        if not (data['correct']):
            if data['profile_expires']:
                data['error'] = 'El código que ingresó ya expiró. Presione Renviar Código ' \
                                'para solicitar uno nuevo.'
    else:
        data['error'] = 'Ha ocurrido un error por favor reingrese sus datos.'

    return JsonResponse(data)


@ensure_csrf_cookie
def validate_pass(request):
    username = request.GET.get('username', None)
    q1 = request.GET.get('question1', None)
    q2 = request.GET.get('question2', None)
    a1 = request.GET.get('answer1', None)
    a2 = request.GET.get('answer2', None)
    password = request.GET.get('password', None)
    ci = request.GET.get('ci', None)

    data = {
        'user_exists': User.objects.filter(username=username).exists()
    }

    if data['user_exists']:
        user = User.objects.get(username=username)

        try:
            activation_key = create_token(8)
            while UserProfile.objects.filter(activationKey=activation_key).count() > 0:
                activation_key = create_token(8)
            c = {'usuario': user.get_full_name,
                 'key': activation_key,
                 'host': request.META['HTTP_HOST']}
            subject = 'Actio Capital - Activación de cuenta'
            message_template = 'register-success-email.html'
            email = user.email
            send_email(subject, message_template, c, email)
        except:
            data['correct'] = False
            return JsonResponse(data)

        user.set_password(password)
        user.save()

        elem_sec = ElemSecurity(question1=q1,
                                answer1=a1,
                                question2=q2,
                                answer2=a2)
        elem_sec.save()

        pass_expires = datetime.datetime.today() + datetime.timedelta(days=180)
        customer = Customer(user=user,
                            ident=ci,
                            elemSecurity=elem_sec,
                            passExpires=pass_expires)
        customer.save()

        key_expires = datetime.datetime.today() + datetime.timedelta(days=1)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.activationKey = activation_key
        user_profile.keyExpires = key_expires
        user_profile.save()

        data['correct'] = True
    else:
        data['error'] = 'Ha ocurrido un error por favor reingrese sus datos.'

    return JsonResponse(data)


@ensure_csrf_cookie
def validate_pass_forgot(request):
    username = request.GET.get('username', None)
    password = request.GET.get('password', None)

    data = {
        'user_exists': User.objects.filter(username=username).exists()
    }

    if data['user_exists']:
        user = User.objects.get(username=username)

        try:
            formato = "%d/%m/%y %I:%M:%S %p"
            date_time = datetime.datetime.today().strftime(formato).split(" ")
            date = date_time[0]
            time = date_time[1] + " " + date_time[2]

            c = {'usuario': user.get_full_name,
                 'fecha': date,
                 'hora': time
                 }

            subject = 'Actio Capital - Cambio de Contraseña Exitoso'
            message_template = 'forgot-pass-email.html'
            email = user.email
            send_email(subject, message_template, c, email)
        except:
            data['correct'] = False
            return JsonResponse(data)

        user.set_password(password)
        user.save()

        pass_expires = datetime.datetime.today() + datetime.timedelta(days=180)
        customer = Customer.objects.get(user=user)
        customer.passExpires = pass_expires
        customer.save()

        data['correct'] = True
    else:
        data['error'] = 'Ha ocurrido un error por favor reingrese sus datos.'

    return JsonResponse(data)


@ensure_csrf_cookie
def old_pass(request):
    username = request.GET.get('username', None)
    password = request.GET.get('pass', None)

    if username == '0':
        user = request.user.id
        username = User.objects.get(pk=user).username

    user = User.objects.get(username=username)

    data = {
        'correct': user.check_password(password)
    }

    return JsonResponse(data)


@ensure_csrf_cookie
def resend_email(request):
    username = request.GET.get('username', None)
    data = {
        'user_exists': User.objects.filter(username=username).exists()
    }

    if data['user_exists']:
        user = User.objects.get(username=username)

        try:
            activation_key = create_token(6)
            while UserProfile.objects.filter(activationKey=activation_key).count() > 0:
                activation_key = create_token(6)
            c = {'usuario': user.get_full_name,
                 'key': activation_key}
            subject = 'Actio Capital - Reenvío de Código'
            message_template = 'confirm-email.html'
            email = user.email
            send_email(subject, message_template, c, email)
            data['envio'] = True
        except:
            data['envio'] = False
            return JsonResponse(data)

        key_expires = datetime.datetime.today() + datetime.timedelta(minutes=2)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.activationKey = activation_key
        user_profile.keyExpires = key_expires
        user_profile.save()

    else:
        data['error'] = 'Ha ocurrido un error por favor reingrese sus datos.'

    return JsonResponse(data)


@ensure_csrf_cookie
def validate_quest(request):
    question = request.GET.get('question', None)
    answer = request.GET.get('answer', None)
    username = request.GET.get('username', None)

    data = {
        'user_exists': User.objects.filter(username=username).exists()
    }

    if data['user_exists']:
        user = User.objects.get(username=username)
        customer = Customer.objects.get(user=user)

        if (customer.elemSecurity.question1 == question) and (customer.elemSecurity.answer1 == answer):
            data['correct'] = True
        elif (customer.elemSecurity.question2 == question) and (customer.elemSecurity.answer2 == answer):
            data['correct'] = True
        else:
            data['correct'] = False
    else:
        data['error'] = 'Ha ocurrido un error por favor reingrese sus datos.'

    return JsonResponse(data)


@ensure_csrf_cookie
def validate_elems(request):
    print(request.user.id)
    quest = request.GET.get('question', None)
    answ = request.GET.get('answer', None)
    f_coord_value = request.GET.get('f_coord_val', None)
    s_coord_value = request.GET.get('s_coord_val', None)
    f_coord = request.GET.get('f_coor', None)
    s_coord = request.GET.get('s_coor', None)

    data = {
        'user_exists': Customer.objects.filter(user=request.user.id).exists(),
        'question': False,
        'coor': False,
        'error': 'Los elementos de seguridad introducidos son incorrectos. '
                 'Verifíque sus datos e intente nuevamente.'
    }

    if data['user_exists']:
        customer = Customer.objects.get(user=request.user.id)
        elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        if (customer.elemSecurity.question1 == quest) and (customer.elemSecurity.answer1 == answ):
            data['question'] = True
        if (customer.elemSecurity.question2 == quest) and (customer.elemSecurity.answer2 == answ):
            data['question'] = True

        print(data['question'])

        if data['question']:
            l = customer.elemSecurity.cardCoor.coor.split(",")
            f = conv_coord(f_coord)
            s = conv_coord(s_coord)

            if l[f] == f_coord_value and l[s] == s_coord_value:
                elems.sessionExpires = True
                print(elems.sessionExpires)
                elems.save()
                data['coor'] = True

    return JsonResponse(data)


@ensure_csrf_cookie
def modify_profile(request):
    q1 = request.GET.get('q1', None)
    q2 = request.GET.get('q2', None)
    a1 = request.GET.get('a1', None)
    a2 = request.GET.get('a2', None)
    email = request.GET.get('email', None)
    password = request.GET.get('password', None)

    data = {
        'user_exists': User.objects.filter(pk=request.user.id).exists(),
        'correct': False,
        'password': False
    }

    if data['user_exists']:
        user = User.objects.get(pk=request.user.id)
        customer = Customer.objects.get(user=user.pk)
        elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        if password != '':
            user.set_password(password)
            data['password'] = True
        if email != '':
            user.email = email
        if q1 != '':
            elems.question1 = q1
        if a1 != '':
            elems.answer1 = a1
        if q2 != '':
            elems.question2 = q2
        if a2 != '':
            elems.answer2 = a2

        elems.save()
        customer.save()
        user.save()

        formato = "%d/%m/%y %I:%M:%S %p"
        date_time = datetime.datetime.today().strftime(formato).split(" ")
        date = date_time[0]
        time = date_time[1] + " " + date_time[2]

        c = {'usuario': user.get_full_name,
             'fecha': date,
             'hora': time
             }

        subject = 'Actio Capital - Cambio en su Perfil de Seguridad'
        message_template = 'modify_profile.html'
        email = user.email
        send_email(subject, message_template, c, email)

        data['correct'] = True
    else:
        data['error'] = 'Ha ocurrido un error por favor reingrese sus datos.'

    return JsonResponse(data)


@ensure_csrf_cookie
def get_cardcoor(request):
    data = {
        'user_exists': User.objects.filter(pk=request.user.id).exists()
    }

    if data['user_exists']:
        user = User.objects.get(pk=request.user.id)
        customer = Customer.objects.get(user=user.pk)

        data['coor'] = [['Tarjeta de Seguridad:'+str(customer.elemSecurity.cardCoor.serial)], [customer.elemSecurity.cardCoor.status]]

    else:
        data['error'] = 'Ha ocurrido un error por favor reingrese sus datos.'

    return JsonResponse(data)


@ensure_csrf_cookie
def status_cardcoor(request):
    serial = request.GET.get('s', None)
    action = request.GET.get('action', None)

    data = {
        'user_exists': User.objects.filter(pk=request.user.id).exists(),
        'correct': False
    }

    if data['user_exists']:
        user = User.objects.get(pk=request.user.id)
        customer = Customer.objects.get(user=user.pk)
        card_coor = CardCoor.objects.get(pk=customer.elemSecurity.cardCoor_id)

        if card_coor.serial == serial:
            formato = "%d/%m/%y %I:%M:%S %p"
            date_time = datetime.datetime.today().strftime(formato).split(" ")
            date = date_time[0]
            time = date_time[1] + " " + date_time[2]

            if action == 'act':
                card_coor.status = True
                subject = 'Actio Capital - Activación de Tarjeta de Seguridad'

                c = {'usuario': customer.user.get_full_name,
                     'fecha': date,
                     'hora': time,
                     'title': 'Activación de Tarjeta de Seguridad',
                     'msg': 'Ha activado su tarjeta de seguridad '
                     }

            else:
                card_coor.status = False
                subject = 'Actio Capital - Desactivación de Tarjeta de Seguridad'

                c = {'usuario': customer.user.get_full_name,
                     'fecha': date,
                     'hora': time,
                     'title': 'Desactivación de Tarjeta de Seguridad',
                     'msg': 'Ha desactivado su tarjeta de seguridad '
                     }

            card_coor.save()

            message_template = 'product_email.html'
            email = customer.user.email
            print('antes de enviar correo coordenadas')
            send_email(subject, message_template, c, email)

            data['correct'] = True
    else:
        data['error'] = 'Ha ocurrido un problema validando sus datos. Intente nuevamente.'

    return JsonResponse(data)


@ensure_csrf_cookie
def send_email_product(request):
    action = request.GET.get('p', None)
    p = action.split(' ')
    data = {}

    customer = Customer.objects.get(user=request.user.id)
    formato = "%d/%m/%y %I:%M:%S %p"
    date_time = datetime.datetime.today().strftime(formato).split(" ")
    date = date_time[0]
    time = date_time[1] + " " + date_time[2]

    c = {'usuario': customer.user.get_full_name,
         'fecha': date,
         'hora': time
         }

    if p[2] == 'act':
        subject = 'Actio Capital - Activación de Producto'
        if p[0] == 'Chequera':
            c['title'] = 'Activación de ' + p[0]
            c['msg'] = 'Activación de ' + p[0] + ' número ' + p[1]
        else:
            c['title'] = 'Activación de TDC'
            c['msg'] = 'Activación de ' + p[0] + ' con terminación ' + p[1]
            c['extra'] = 'Ya puede usar su TDC en cualquier establecimiento como método de pago.'
    else:
        subject = 'Actio Capital - Desactivación de Producto'
        if p[0] == 'Chequera':
            c['title'] = 'Desactivación de ' + p[0]
            c['msg'] = 'Desactivación de ' + p[0] + ' número ' + p[1]
            c['extra'] = 'Recuerde que todos los cheques pertenecientes a esta chequera fueron anulados. ' \
                         'Por lo tanto, no son válidos.'
        else:
            c['title'] = 'Desactivación de TDC'
            c['msg'] = 'Desactivación de ' + p[0] + ' con terminación ' + p[1]
            c['extra'] = 'Recuerde que ya no puede usar su TDC como método de pago, hasta que la active nuevamente.'

    message_template = 'product_email.html'
    email = customer.user.email
    print('antes de enviar correo coordenadas')
    send_email(subject, message_template, c, email)

    return JsonResponse(data)


def send_email(subject, message_template, context, email):
    from_email = 'Actio Capital'
    email_subject = subject
    message = get_template(message_template).render(context)
    msg = EmailMessage(email_subject, message, to=[email], from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    print("Se envió exitosamente el correo.")


def email_login_successful(user):
    usuario = user.get_full_name()
    formato = "%d/%m/%y %I:%M:%S %p"
    date_time = user.last_login.strftime(formato).split(" ")
    date = date_time[0]
    time = date_time[1] + " " + date_time[2]

    c = {'usuario': usuario,
         'fecha': date,
         'hora': time}

    subject = 'Actio Capital - Inicio de Sesión Exitoso'
    message_template = 'email_login.html'
    send_email(subject, message_template, c, user.email)


def user_block(user):
    try:
        user.is_active = False
        user.save()
        c = {'usuario': user.get_full_name}
        subject = 'Actio Capital - Cuenta Desactivada '
        message_template = 'account_block.html'
        email = user.email
        send_email(subject, message_template, c, email)
    except:
        pass


def create_token(num):
    chars = list('ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwyz0123456789')
    random.shuffle(chars)
    chars = ''.join(chars)
    sha1 = hashlib.sha1(chars.encode('utf8'))
    token = sha1.hexdigest()
    key = token[:num]
    return key


def list_list(char):
    l = char.split(",")
    l = list(map(int, l))
    a = []
    for num in range(0, 25, 6):
        a.append(l[num:num+6])
    return a


def new_token(request, pk):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('logout'))

    user = User.objects.get(pk=pk)
    UserProfile.objects.filter(user=user).delete()
    key = create_token(8)
    key_expires = datetime.datetime.today() + datetime.timedelta(days=1)
    new_profile = UserProfile(user=user, activationKey=key,
                              keyExpires=key_expires)
    try:
        c = {'usuario': user.get_full_name,
             'key': key,
             'host': request.META['HTTP_HOST']}
        subject = 'Actio Capital - Código Activación de cuenta'
        message_template = 'register-success-email.html'
        email = user.email
        send_email(subject, message_template, c, email)
    except:
        render(request, 'register_success.html')

    new_profile.save()
    return render(request, 'register_success.html')


def register_confirm(request, activation_key):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('logout'))

    user_profile = get_object_or_404(UserProfile,
                                     activationKey=activation_key)
    user = user_profile.user

    time = datetime.datetime.today()

    if user_profile.keyExpires < time:
        return HttpResponseRedirect(reverse_lazy('new_Token',
                                                 kwargs={'pk': user.pk}))

    c = {'usuario': user.get_full_name,
         'host': request.META['HTTP_HOST']}

    if request.method == 'GET':
        user.is_active = True
        user.save()
        try:
            subject = 'Actio Capital - Cuenta Activada'
            message_template = 'account-active.html'
            email = user.email
            send_email(subject, message_template, c, email)
        except:
            pass

    return render(request, 'acc-active.html')


def authenticate_user(username=None):
    try:
        user = User.objects.get(username=username)
        if user is not None:
            return user
    except User.DoesNotExist:
        return None


def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('salir'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username == "" or password == "":
                msg = ""
                if username == "":
                    msg = msg + "  Introduzca su número de tarjeta. "

                if password == "":
                    msg = msg + " Introduzca su contraseña. "

                form.add_error(None, msg)
                context = {'form': form}
                return render(request, 'base-index.html', context)

            msg_error = " Recuerde: Al realizar tres intentos erróneos su cuenta será bloqueada."
            error_username = "Tu número de tarjeta  o contraseña no son correctos." + msg_error
            user_auth = authenticate_user(username)

            if user_auth is not None:
                users = User.objects.get(username=username)
                user_profile = get_object_or_404(UserProfile, user=users)
                customer = Customer.objects.get(user=users)
                today = datetime.datetime.today().date()
                if users.is_active and user_profile.intent < 3:
                    user = authenticate(username=users.username,
                                        password=password)
                    if user:
                        if customer.passExpires <= today:
                            msg = "Su contraseña ha expirado por favor ingrese sus datos para cambiar su contraseña."
                            form.add_error(None, msg)

                            context = {'form': form}
                            return render(request, 'forgot_password.html', context)

                        last_login = users.last_login
                        login(request, user)
                        # email_login_successful(user)
                        if not(customer.elemSecurity.cardCoor_id is None):
                            elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)
                            elems.sessionExpires = False
                            elems.save()

                        user_profile.intent = 0
                        user_profile.save()
                        customer.lastLogin = last_login
                        customer.ref = str(datetime.datetime.today().microsecond)[:5] + str(customer.id)
                        customer.save()
                        return HttpResponseRedirect(reverse_lazy('inicio',
                                                                 kwargs={'pk': customer.ref}))
                    else:
                        form.add_error(None, error_username)

                        if user_profile.dateIntent != today:
                            user_profile.intent = 1
                            user_profile.dateIntent = today
                        else:
                            user_profile.intent = user_profile.intent + 1
                            if user_profile.intent == 3:
                                msg = "Su cuenta ha sido bloqueada. Comuniquese con atención al cliente" \
                                      " para iniciar el proceso de desbloqueo."
                                form.add_error(None, msg)
                                user_block(users)
                        user_profile.save()
                elif user_profile.intent == 3:
                    msg = "Su cuenta se encuentra bloqueada. Comuniquese con atención al cliente" \
                          " para iniciar el proceso de desbloqueo."
                    form.add_error(None, msg)
                else:
                    msg = "Aún no ha activado su cuenta. Por favor revise su correo."
                    form.add_error(None, msg)
                    user = None
            else:
                form.add_error(None, error_username)
        else:
            context = {'form': form}
            return render(request, 'base-index.html', context)
    else:
        form = LoginForm()

    context = {'form': form, 'host': request.get_host()}
    return render(request, 'base-index.html', context)


class Home(TemplateView):
    template_name = 'base-index.html'


class Home_Client(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Home_Client, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]

        return context


class Logout(TemplateView):
    template_name = 'logout.html'


class Register_success(TemplateView):
    template_name = 'register_success.html'


class Account_activate(TemplateView):
    template_name = 'acc-active.html'


class Restore_pass_success(TemplateView):
    template_name = 'restore_pass_success.html'


class Register(TemplateView):
    template_name = 'register.html'


class Active(TemplateView):
    template_name = 'account-active.html'


class Restore_pass(TemplateView):
    template_name = 'forgot_password.html'


class Account(LoginRequiredMixin, TemplateView):
    template_name = 'accounts.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Account, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]
        context['acc_id'] = self.kwargs['acc_id']
        return context


class Tdc(LoginRequiredMixin, TemplateView):
    template_name = 'tdc.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Tdc, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]
        return context


class Loans(LoginRequiredMixin, TemplateView):
    template_name = 'loans.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Loans, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]
        return context


class Transfer_my_acc(LoginRequiredMixin, TemplateView):
    template_name = 'trans_my_acc.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Transfer_my_acc, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]

        context['customer'] = customer
        return context


class Transfer_my_bank(LoginRequiredMixin, TemplateView):
    template_name = 'trans_my_bank.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Transfer_my_bank, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        if elems.sessionExpires:
            context['session'] = 'true'
        else:
            quest1 = customer.elemSecurity.question1
            quest2 = customer.elemSecurity.question2
            num = random.randint(1, 2)
            if num == 1:
                context['question'] = quest1
            else:
                context['question'] = quest2

            a = list('ABCDEF')
            random.shuffle(a)
            b = list('12345')
            random.shuffle(b)
            context['first_coor'] = a[0] + b[0]
            context['second_coor'] = a[1] + b[1]
            context['session'] = 'false'

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]
        context['affiliate'] = Affiliate.objects.filter(customer=customer.pk,
                                                        bank='BANCO ACTIO CAPITAL, C.A.')

        return context


class Transfer_others_bank(LoginRequiredMixin, TemplateView):
    template_name = 'trans_other_bank.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Transfer_others_bank, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        if elems.sessionExpires:
            context['session'] = 'true'
        else:
            quest1 = customer.elemSecurity.question1
            quest2 = customer.elemSecurity.question2
            num = random.randint(1, 2)
            if num == 1:
                context['question'] = quest1
            else:
                context['question'] = quest2

            a = list('ABCDEF')
            random.shuffle(a)
            b = list('12345')
            random.shuffle(b)
            context['first_coor'] = a[0] + b[0]
            context['second_coor'] = a[1] + b[1]
            context['session'] = 'false'

        context['customer'] = customer
        context['affiliate'] = Affiliate.objects.filter(customer=customer.pk).exclude(bank='BANCO ACTIO CAPITAL, C.A.')
        return context


class DataTransfer(LoginRequiredMixin, TemplateView):
    template_name = 'transfer-data.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            DataTransfer, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Success(LoginRequiredMixin, TemplateView):
    template_name = 'transfer-success.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Success, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Payments(LoginRequiredMixin, TemplateView):
    template_name = 'payments.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Payments, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class DataPayment(LoginRequiredMixin, TemplateView):
    template_name = 'payment-data.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            DataPayment, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Success_Payments(LoginRequiredMixin, TemplateView):
    template_name = 'payments-success.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Success_Payments, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Register_Affiliate(LoginRequiredMixin, TemplateView):
    template_name = 'register-affiliate.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Register_Affiliate, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer

        return context


class Register_Services(LoginRequiredMixin, TemplateView):
    template_name = 'register-services.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Register_Services, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Request(LoginRequiredMixin, TemplateView):
    template_name = 'request.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        card_coor = ElemSecurity.objects.get(pk=customer.elemSecurity_id).cardCoor_id

        if card_coor is None:
            context['card_coor'] = True
        else:
            context['card_coor'] = CardCoor.objects.get(pk=card_coor).status is False

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]

        return context


class Request_Coord(LoginRequiredMixin, TemplateView):
    template_name = 'req-tar-coor.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request_Coord, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        elem = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        coor = ''
        for i in range(0, 30):
            num = random.randint(0, 999)
            if i < 29:
                coor = coor + str(num).zfill(3) + ','
            else:
                coor = coor + str(num).zfill(3)

        serial = str(random.randint(1, 10000000)).zfill(7)

        if elem.cardCoor_id is None:
            card_cord = CardCoor(serial=serial,
                                 coor=coor)
            card_cord.save()
            elem.cardCoor_id = card_cord.pk
            elem.save()

        else:
            card_cord = CardCoor.objects.get(pk=elem.cardCoor_id)
            card_cord.serial = serial
            card_cord.coor = coor
            card_cord.status = True
            card_cord.save()

            formato = "%d/%m/%y %I:%M:%S %p"
            date_time = datetime.datetime.today().strftime(formato).split(" ")
            date = date_time[0]
            time = date_time[1] + " " + date_time[2]

            c = {'usuario': customer.user.get_full_name,
                 'fecha': date,
                 'hora': time,
                 'title': 'Generación de Tarjeta de Seguridad',
                 'msg': 'Ha generado una nueva tarjeta de seguridad '
                 }

            subject = 'Actio Capital - Generación de Tarjeta de Seguridad'
            message_template = 'product_email.html'
            email = customer.user.email
            print('antes de enviar correo coordenadas')
            send_email(subject, message_template, c, email)

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]
        context['coor'] = list_list(coor)

        return context


class Request_Checkbook(LoginRequiredMixin, TemplateView):
    template_name = 'req-checkb.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request_Checkbook, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        if elems.sessionExpires:
            context['session'] = 'true'
        else:
            quest1 = customer.elemSecurity.question1
            quest2 = customer.elemSecurity.question2
            num = random.randint(1, 2)
            if num == 1:
                context['question'] = quest1
            else:
                context['question'] = quest2

            a = list('ABCDEF')
            random.shuffle(a)
            b = list('12345')
            random.shuffle(b)
            context['first_coor'] = a[0] + b[0]
            context['second_coor'] = a[1] + b[1]
            context['session'] = 'false'

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]

        return context


class Request_Appointment(LoginRequiredMixin, TemplateView):
    template_name = 'req-appointment.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request_Appointment, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Request_References(LoginRequiredMixin, TemplateView):
    template_name = 'req-reference.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request_References, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Request_References_Success(LoginRequiredMixin, TemplateView):
    template_name = 'req-reference_success.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request_References_Success, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Request_Appointment_Success(LoginRequiredMixin, TemplateView):
    template_name = 'req-appointment_success.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request_Appointment_Success, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Request_Checkbook_Success(LoginRequiredMixin, TemplateView):
    template_name = 'req-checkb_success.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Request_Checkbook_Success, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context


class Management(LoginRequiredMixin, TemplateView):
    template_name = 'management-products.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Management, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        if elems.sessionExpires:
            context['session'] = 'true'
        else:
            quest1 = customer.elemSecurity.question1
            quest2 = customer.elemSecurity.question2
            num = random.randint(1, 2)
            if num == 1:
                context['question'] = quest1
            else:
                context['question'] = quest2

            a = list('ABCDEF')
            random.shuffle(a)
            b = list('12345')
            random.shuffle(b)
            context['first_coor'] = a[0] + b[0]
            context['second_coor'] = a[1] + b[1]
            context['session'] = 'false'

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]

        return context


class Profile(LoginRequiredMixin, TemplateView):
    template_name = 'profile-security.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Profile, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])
        elems = ElemSecurity.objects.get(pk=customer.elemSecurity_id)

        if elems.sessionExpires:
            context['session'] = 'true'
        else:
            quest1 = customer.elemSecurity.question1
            quest2 = customer.elemSecurity.question2
            num = random.randint(1, 2)
            if num == 1:
                context['question'] = quest1
            else:
                context['question'] = quest2

            a = list('ABCDEF')
            random.shuffle(a)
            b = list('12345')
            random.shuffle(b)
            context['first_coor'] = a[0] + b[0]
            context['second_coor'] = a[1] + b[1]
            context['session'] = 'false'

        context['customer'] = customer
        context['num'] = customer.user.username[:10]
        context['num2'] = customer.user.username[10:]

        return context

        # def post(self, request, *args, **kwargs):
        #     """
        #     Handles POST requests, instantiating a form instance with the passed
        #     POST variables and then checked for validity.
        #     """
        #     form = ProfileForm(request.POST)
        #     customer = Customer.objects.get(ref=self.kwargs['pk'])
        #
        #     if form.is_valid():
        #         email = form.cleaned_data['email']
        #         f_quest = form.cleaned_data['first_quest']
        #
        #         if email == "" or f_quest == "":
        #             msg = ""
        #             if username == "":
        #                 msg = msg + "  Introduzca su número de tarjeta. "
        #
        #             if password == "":
        #                 msg = msg + " Introduzca su contraseña. "
        #
        #             form.add_error(None, msg)
        #
        #             context = {'form': form,
        #                        'pk': self.kwargs['pk'],
        #                        'customer': customer}
        #             return render(request, 'profile-security.html', context)
        #
        #     else:
        #         print('else')
        #         context = {'form': form,
        #                    'pk': self.kwargs['pk'],
        #                    'customer': customer}
        #         return render(request, 'profile-security.html', context)


class Help(LoginRequiredMixin, TemplateView):
    template_name = 'help.html'
    login_url = 'home'
    redirect_field_name = 'logout'

    def get_context_data(self, **kwargs):
        context = super(
            Help, self).get_context_data(**kwargs)

        customer = Customer.objects.get(ref=self.kwargs['pk'])

        context['customer'] = customer
        return context



