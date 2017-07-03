from django.conf.urls import url
import django.contrib.auth.views
from ob_app.views import *


urlpatterns = [
    url(
        r'^$',
        Home.as_view(),
        name='home'),
    url(
        r'^inicio',
        Home_Client.as_view(),
        name='inicio'),
    url(
        r'^salir',
        django.contrib.auth.views.logout,
        {
            'next_page': 'home'
        },
        name='salir'),
    url(
        r'^registro-exitoso',
        Register_success.as_view(),
        name='registro-exitoso'),
    url(
        r'^nueva-pass-exitosa',
        Restore_pass_success.as_view(),
        name='nueva-pass-exitosa'),
    url(
        r'^registro-usuario',
        Register.as_view(),
        name='registro'),
    url(
        r'^restablecer-pass',
        Restore_pass.as_view(),
        name='restablecer-pass'),
    url(
        r'^consultar-cuenta/(?P<pk>\d+)/',
        Account.as_view(),
        name='consultar-cuenta'),
    url(
        r'^consultar-tdc/(?P<pk>\d+)/',
        Tdc.as_view(),
        name='consultar-tdc'),
    url(
        r'^consultar-prestamo/(?P<pk>\d+)/',
        Loans.as_view(),
        name='consultar-prestamo'),
    url(
        r'^transf-mis-cuentas',
        Transfer_my_acc.as_view(),
        name='transf-mis-cuentas'),
    url(
        r'^transf-mi-banco',
        Transfer_my_bank.as_view(),
        name='transf-mi-banco'),
    url(
        r'^transf-otros-bancos',
        Transfer_others_bank.as_view(),
        name='transf-otros-bancos'),
    url(
        r'^datos-transferencia/(?P<pk>\d+)/',
        DataTransfer.as_view(),
        name='datos-transferencia'),
    url(
        r'^transferencia-exitosa',
        Success.as_view(),
        name='transferencia-exitosa'),
    url(
        r'^pagos',
        Payments.as_view(),
        name='pagos'),
    url(
        r'^datos-pago/(?P<pk>\d+)/',
        DataPayment.as_view(),
        name='datos-pago'),
    url(
        r'^pago-exitoso',
        Success_Payments.as_view(),
        name='pago-exitoso'),
    url(
        r'^registro-afiliados',
        Register_Affiliate.as_view(),
        name='registro-afiliados'),
    url(
        r'^registro-servicios',
        Register_Services.as_view(),
        name='registro-servicios'),
    url(
        r'^solicitudes$',
        Request.as_view(),
        name='solicitudes'),
    url(
        r'^solicitudes/Tarjeta-Coordenadas$',
        Request_Coord.as_view(),
        name='solicitud-tarjeta-coordenadas'),
    url(
        r'^solicitudes/Chequeras$',
        Request_Checkbook.as_view(),
        name='solicitud-chequeras'),
    url(
        r'^solicitudes/Cita$',
        Request_Appointment.as_view(),
        name='solicitud-citas'),
    url(
        r'^solicitudes/Referencias$',
        Request_References.as_view(),
        name='solicitud-referencias'),
    url(
        r'^solicitudes/Cita/exitosa',
        Request_Appointment_Success.as_view(),
        name='solicitud-citas-exitosa'),
    url(
        r'^solicitudes/Chequeras/exitosa',
        Request_Checkbook_Success.as_view(),
        name='solicitud-chequeras-exitosa'),
    url(
        r'^solicitudes/Referencias/exitosa',
        Request_References_Success.as_view(),
        name='solicitud-referencias-exitosa'),
    url(
        r'^gestion-productos',
        Management.as_view(),
        name='gestion-productos'),
    url(
        r'^perfil-seguridad',
        Profile.as_view(),
        name='perfil-seguridad'),
    url(
        r'^ayuda',
        Help.as_view(),
        name='ayuda'),
]