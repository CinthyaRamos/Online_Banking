/**
 * Created by CinthyaCarolina on 16/6/2017.
 */

var balance = [];


$(document).ready(function (){
    $('li').removeClass("active");

    $("#account").change(function () {
        if ($("#account").val() !== '0') {
            $.each(balance,function (i,val) {
                if (val[0] === 'Ahorro' && $("#account").val() === '1'){
                    $("#balance_transf").text(val[1])
                }
                else if (val[0] === 'Corriente' && $("#account").val() === '2'){
                    $("#balance_transf").text(val[1])
                }
            });

            $("#balance_transf").css({display:'inline-block'});
        }
        else {
            $("#balance_transf").css({display: 'none'});
        }
        $("#account").removeClass('errors');
    });

    $("#amount_transf").click(function () {
        $("#amount_transf").removeClass('errors');
    });

    $("#amount_payment").click(function () {
        $("#amount_payment").removeClass('errors');
    });

    $("#descrip_transf").click(function () {
        $("#descrip_transf").removeClass('errors');
    });

    $("#descrip_payment").click(function () {
        $("#descrip_payment").removeClass('errors');
    });

});


function drop_account_trans(account){
    var path = document.referrer.split('/');
    var key = path[5];
    alert(key);
    var avaliable;

    $("#account").empty();
    $("#amount_transf").empty();

    $.each(account,function (i,val) {
        if ((key === '0' || typeof(key) === "undefined") && i === 0) {
            $("#account").append('<option value="'+'0'+'" selected> '+"Seleccione"+'</option>');
        }
        if (val[0].includes("Ahorro")) {
            avaliable = ['Ahorro',val[3][0]];
            balance.push(avaliable);
        }
        if (val[0].includes("Corriente")) {
            avaliable = ['Corriente',val[3][0]];
            balance.push(avaliable);
        }
        if (key === '1' && val[0].includes("Ahorro")) {
            $("#account").append('<option value="'+(i+1)+'" selected> '+val[0].substring(6)+'  '+val[1].substring(12)+'</option>');
            $("#account").append('<option value="'+'0'+'"> '+"Seleccione"+'</option>');
            $("#balance_transf").text(val[3][0]);
        }
        else if (key === '2' && val[0].includes("Corriente")) {
            $("#account").append('<option value="'+(i+1)+'" selected> '+val[0].substring(6)+'  '+val[1].substring(12)+'</option>');
            $("#account").append('<option value="'+'0'+'"> '+"Seleccione"+'</option>');
            $('#balance_transf').text(val[3][0]);
        }
        else {
            $("#account").append('<option value="'+(i+1)+'"> '+val[0].substring(6)+'  '+val[1].substring(12)+'</option>');
        }
    });
}


function send_transfer(a,b,c,d,e,aff) {
    var msg = '';
    var available = parseFloat($("#balance_transf").text().replace(/\./g, '').replace(',','.'));
    var regexLetters = /^[a-zA-ZáéíóúàèìòùÀÈÌÒÙÁÉÍÓÚñÑüÜ\s ]*$/;
    if ($(a).val() === '0') {
        $(a).addClass('errors');
        msg = 'Seleccione una cuenta a debitar';
    }
    else if ($(c).val() === ''){
        $(c).addClass('errors');
        msg = 'El monto de la transferencia no puede estar vacío.';
    }
    else if (!($.isNumeric($(c).val()))) {
        $(c).addClass('errors');
        msg = 'El monto de la transferencia debe ser un número válido. ' +
            'Por ejemplo: 23989.99, donde con el punto se indican los decimales.';
    }
    else if (parseFloat($(c).val()) > available) {
        $(c).addClass('errors');
        msg = 'El monto de la transferencia no puede ser mayor su monto disponible.';
    }
    else if ($(d).val() === '') {
        $(d).addClass('errors');
        msg = 'La descripción no puede estar vacía.';
    }
    else if (!($(d).val().match(regexLetters))){
        $(d).addClass('errors');
        msg = 'La descripción solo admite letras.';
    }
    if (msg !== ''){
        notification_error(msg);
    }
    else {
        var url = document.referrer.split('/');
        var url_api = url[0] + "/" + url[1] + "/localhost:8001/ajax/send-transfer/";
        var acc = document.getElementById('account').options[document.getElementById('account').selectedIndex].text;
        var acc_dest;
        if (url[4] === 'transf-mi-banco') {
            acc_dest = b;
        }
        else {
            $.getJSON('../../../static/js/bank.json', function (data) {
                $.each( data, function( key, val ) {
                    if ($.trim($('#acc_transf').text()).substring(0,4) === val.codigo) {
                        alert(val.banco.replace(/\s/g,'_'));
                        acc_dest = $.trim($('#name_transf').text()).replace(/\s/g,'_') + ' ' + val.banco.replace(/\s/g,'_');
                    }
                });
            });
        }
        notification_success('Transacción en proceso....');
        setTimeout(function(){
            $.ajax({
                url: url_api,
                origin: 'localhost:8000',
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                data: {
                    acc_source: acc,
                    acc_dest: acc_dest,
                    amount: $(c).val(),
                    detail: $(d).val(),
                    num: e,
                    type: url[4]
                },
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    if (!data.success) {
                        notification_error('Transferencia no exitosa. Intente más tarde.');
                    }
                    else{
                        var path = window.location.href.split('/');
                        notification_success(data.msg);
                        send_email('send',url[4],data.amount, data.ref, aff, acc);
                        send_email(0,url[4],data.amount, data.ref, aff, '');
                        setTimeout(function(){
                            location.href = url[0] + "/" + url[1] + "/" + url[2] + "/" + url[3] + "/transferencia-exitosa/"
                                + path[5] + '/' + data.ref + '/';
                        }, 3000);
                    }
                },
                error: function (data) {
                    alert("Lo sentimos, hay problemas con el servidor. Intente más tarde.");
                }
            })
        }, 1000);
    }
}


function send_email(a,b,c,d,e,f) {
    var path = window.location.href.split('/');
    var url = path[0] + "/" + path[1] + "/" + path[2] + "/ajax/send-emails/";

    $.ajax({
        url: url,
        origin: 'localhost:8000',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        type: 'GET',
        dataType: 'json',
        data: {
            type:a,
            t: b,
            amount: c,
            ref: d,
            aff: e,
            acc : f
        }
    })
}


function pay_services(a,b,c,d,e,f,aff) {
    var msg = '';
    var available = parseFloat($("#balance_transf").text().replace(/\./g, '').replace(',','.'));
    var regexLetters = /^[a-zA-ZáéíóúàèìòùÀÈÌÒÙÁÉÍÓÚñÑüÜ\s ]*$/;
    if ($(a).val() === '0') {
        $(a).addClass('errors');
        msg = 'Seleccione una cuenta a debitar';
    }
    else if ($(d).val() === ''){
        $(d).addClass('errors');
        msg = 'El monto de la transferencia no puede estar vacío.';
    }
    else if (!($.isNumeric($(d).val()))) {
        $(d).addClass('errors');
        msg = 'El monto de la transferencia debe ser un número válido. ' +
            'Por ejemplo: 23989.99, donde con el punto se indican los decimales.';
    }
    else if (parseFloat($(d).val()) > available) {
        $(d).addClass('errors');
        msg = 'El monto de la transferencia no puede ser mayor su monto disponible.';
    }
    else if ($(e).val() === '') {
        $(e).addClass('errors');
        msg = 'La descripción no puede estar vacía.';
    }
    else if (!($(e).val().match(regexLetters))){
        $(e).addClass('errors');
        msg = 'La descripción solo admite letras.';
    }
    if (msg !== ''){
        notification_error(msg);
    }
    else {
        var url = document.referrer.split('/');
        var url_api = url[0] + "/" + url[1] + "/localhost:8001/ajax/pay-services/";
        var acc = document.getElementById('account').options[document.getElementById('account').selectedIndex].text;
        var dest = $.trim($(c).text()).split(' ');
        if (dest.length > 2){
            dest = dest[1] + ' ' + dest[2]
        }
        else{
            dest = dest[1]
        }
        notification_success('Transacción en proceso....');
        setTimeout(function(){
            $.ajax({
                url: url_api,
                origin: 'localhost:8000',
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                data: {
                    acc: acc,
                    service: $.trim($(b).text()),
                    product: dest,
                    amount: $(d).val(),
                    detail: $(e).val() + ', ' + $.trim($(c).text()),
                    num: f
                },
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    if (!data.success) {
                        notification_error('Pago de servicio no exitoso. Intente más tarde.');
                    }
                    else{
                        var path = window.location.href.split('/');
                        notification_success(data.msg);
                        send_email('send',url[4],data.amount, data.ref, aff, acc);
                        send_email(0,url[4],data.amount, data.ref, aff, '');
                        setTimeout(function(){
                            location.href = url[0] + "/" + url[1] + "/" + url[2] + "/" + url[3] + "/transferencia-exitosa/"
                                + path[5] + '/' + data.ref + '/';
                        }, 3000);
                    }
                },
                error: function (data) {
                    alert("Lo sentimos, hay problemas con el servidor. Intente más tarde.");
                }
            })
        }, 1000);
    }
    
}


