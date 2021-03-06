/**
 * Created by Cinthya C. Ramos G. on 13/7/2017.
*/

$(document).ready(function () {
    var regexNum =  /[0-9]+/;
    var regexRepeat = /(.)\1{2,}/;
    var regexMay = /[A-Z]+/;
    var regexMin = /[a-z]+/;
    var regexSpecial = /[$!%.#_*?&]+/;
    var numtarj = '#numtarj';
    var ccv = '#ccv';
    var ci = '#ci';
    var email = '#email';
    var cod = '#cod';
    var answer = '#answer';
    var password = '#password';
    var confirm = '#confirm-pass';
    var first_name = $("#name_customer").text().split(' ');
    var last_name = $("#last-name_customer").text().split(' ');
    var ci_cust = $("#ci_customer").text().split('-');
    var phone_home = $("#phone-home").text().split('-');
    var cellphone = $("#cellphone").text().split('-');
    var phone_office = $("#phone-office").text().split('-');
    var birthday = $("#birthday").text();
    var birthday_split = $("#birthday").text().split('-');
    var msj_num = "Sólo se admiten números";
    var msj = "Este campo es obligatorio";

    $('#month').on('focus', function () {
        $('#month').removeClass('errors');
    });

    $('#year').on('focus', function () {
        $('#year').removeClass('errors');
    });

    $(numtarj).on('focusout', function () {
        if ( $(numtarj).val() !== ""){
            if ( !($(numtarj).val().match(regexNum))) {
                $('#error-num-tarj').text(msj_num);
                $(numtarj).addClass('errors');
            }
            else if ($(numtarj).val().length < 18){
                $('#error-num-tarj').text("Debe contener 18 dígitos");
                $(numtarj).addClass('errors');
            }
            else{
                $(numtarj).removeClass('errors');
                $(numtarj).css({border: '2px solid #d2d6de'});
                $('#error-num-tarj').empty();
            }
        }
        else if ($(numtarj).val() === ""){
            $('#error-num-tarj').text(msj);
            $(numtarj).addClass('errors');
        }
    });

    $(numtarj).on('focus', function () {
        $(numtarj).removeClass('errors');
        $(numtarj).css({'border-color': '#8AB7B6'});
        $('#error-num-tarj').empty();
        $("#error-general").empty();
        $("#error").empty();
    });

    $(ccv).on('focusout', function () {
        if ( $(ccv).val() !== ""){
            if ( !($(ccv).val().match(regexNum))) {
                $('#error-ccv').text(msj_num);
                $(ccv).addClass('errors');
            }
            else if ($(ccv).val().length < 3){
                $('#error-ccv').text("Debe contener 3 dígitos");
                $(ccv).addClass('errors');
            }
            else{
                $(ccv).css({border: '2px solid #d2d6de'});
                $(ccv).removeClass('errors');
                $('#error-ccv').empty();
            }
        }
        else if ($(ccv).val() === ""){
            $('#error-ccv').text(msj);
            $(ccv).addClass('errors');
        }
    });

    $(ccv).on('focus', function () {
        $(ccv).removeClass('errors');
        $(ccv).css({'border-color': '#8AB7B6'});
        $('#error-ccv').empty();
        $("#error-general").empty();
        $("#error").empty();
    });

    $(ci).on('focusout', function () {
        if ( $(ci).val() !== ""){
            if ( !($(ci).val().match(regexNum))) {
                $('#error-ci').text(msj_num);
                $(ci).addClass('errors');
            }
            else if ($(ci).val().length < 6){
                $('#error-ci').text("Debe contener mínimo 6 dígitos");
                $(ci).addClass('errors');
            }
            else{
                $(ci).css({border: '2px solid #d2d6de'});
                $(ci).removeClass('errors');
                $('#error-ci').empty();
            }
        }
        else if ($(ci).val() === ""){
            $('#error-ci').text(msj);
            $(ci).addClass('errors');
        }
    });

    $(ci).on('focus', function () {
        $(ci).removeClass('errors');
        $(ci).css({'border-color': '#8AB7B6'});
        $('#error-ci').empty();
        $("#error-general").empty();
        $("#error").empty();
    });

    $(answer).keyup( function () {
        if ( $(answer).val() !== ""){
            $(answer).css({border: '2px solid #d2d6de'});
            $(answer).removeClass('errors');
            $('#error-answer').empty();
        }
        else {
            $('#error-answer').text(msj);
            $(answer).addClass('errors');
        }
    });

    $(answer).on('focus', function () {
        $(answer).removeClass('errors');
        $(answer).css({'border-color': '#8AB7B6'});
        $('#error-answer').empty();
    });

    $(password).keyup( function () {
        if ( $(password).val() !== ""){
            var path = window.location.href.split('/');
            var url_api = path[0]+"/"+path[1]+"/"+path[2]+"/ajax/validate_passw/";
            $.ajax({
                url: url_api,
                origin: 'localhost:8000',
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                data: {
                    username: $(numtarj).val(),
                    pass: $(password).val()
                },
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    if (data.correct) {
                       if (!($('#old').hasClass('text-danger'))) {
                            $('#old').addClass('text-danger');
                        }
                        $('#old').removeClass('text-success');
                        $(password).addClass('errors'); 
                    }
                    else {
                        $('#old').removeClass('text-danger');
                        $('#old').addClass('text-success');
                           
                    }
                },
                error: function (data) {
                    alert("Lo sentimos, hay problemas con el servidor. Intente más tarde.");
                }
            })

            if ( ($(password).val().match(regexRepeat))) {
                if (!($('#repeat-carac').hasClass('text-danger'))) {
                    $('#repeat-carac').addClass('text-danger');
                }
                $('#repeat-carac').removeClass('text-success');
                $(password).addClass('errors');
            }
            else {
                $('#repeat-carac').removeClass('text-danger');
                $('#repeat-carac').addClass('text-success');
                  
            }
            if ( data_customer($(password).val()) ) {
                if (!($('#pers-carac').hasClass('text-danger'))) {
                    $('#pers-carac').addClass('text-danger');
                }
                $('#pers-carac').removeClass('text-success');
                $(password).addClass('errors');
            }
            else {
                $('#pers-carac').removeClass('text-danger');
                $('#pers-carac').addClass('text-success');
                  
            }
            if ( $(password).val().match(regexNum) ) {
                $('#num-carac').removeClass('text-danger');
                $('#num-carac').addClass('text-success');
                  
            }
            else {
                if (!($('#num-carac').hasClass('text-danger'))) {
                    $('#num-carac').addClass('text-danger');
                }
                $('#num-carac').removeClass('text-success');
                $(password).addClass('errors');
            }
            if ( !($(password).val().match(regexMin)) ) {
                if (!($('#carac').hasClass('text-danger'))) {
                    $('#carac').addClass('text-danger');
                }
                $('#carac').removeClass('text-success');
                $(password).addClass('errors');
            }
            else {
                $('#carac').removeClass('text-danger');
                $('#carac').addClass('text-success');
                  
            }
            if ( !($(password).val().match(regexMay)) ) {
                if (!($('#carac').hasClass('text-danger'))) {
                    $('#carac').addClass('text-danger');
                }
                $('#carac').removeClass('text-success');
                $(password).addClass('errors');
            }
            else {
                $('#carac').removeClass('text-danger');
                $('#carac').addClass('text-success');
                  
            }
            if ( $(password).val().length < 8) {
                if (!($('#min-carac').hasClass('text-danger'))) {
                    $('#min-carac').addClass('text-danger');
                }
                $('#min-carac').removeClass('text-success');
                $(password).addClass('errors');
            }
            else{
                $('#min-carac').removeClass('text-danger');
                $('#min-carac').addClass('text-success');
                  
            }
            if ( !($(password).val().match(regexSpecial)) ) {
                if (!($('#spec-carac').hasClass('text-danger'))) {
                    $('#spec-carac').addClass('text-danger');
                }
                $('#spec-carac').removeClass('text-success');
                $(password).addClass('errors');
            }
            else{
                $('#spec-carac').removeClass('text-danger');
                $('#spec-carac').addClass('text-success');
                  
            }
            if ( $(confirm).val() !== $(password).val()) {
                $('#confirm').removeClass('text-success');
                if ( !($('#confirm').hasClass('text-danger')) ) {
                    $('#confirm').addClass('text-danger');
                }
                $(confirm).addClass('errors');
            }
            else{
                $(confirm).css({border: '2px solid #d2d6de'});
                $(confirm).removeClass('errors');
                $('#confirm').removeClass('text-danger');
                $('#confirm').addClass('text-success');
                $('#error-conf-pass').empty();
            }
            if ( ($('#old').hasClass('text-danger')) || ($('#spec-carac').hasClass('text-danger')) ||
            ($('#min-carac').hasClass('text-danger')) || ($('#carac').hasClass('text-danger')) ||
            ($('#pers-carac').hasClass('text-danger')) || ($('#num-carac').hasClass('text-danger')) || 
            ($('#repeat-carac').hasClass('text-danger')) ) {
                $(password).css({border: '2px solid #d2d6de'});
                $(password).removeClass('errors');
                $('#error-pass').empty();
            }
        }
        else {
            $('#error-pass').text("Este campo tiene errores");
            $(password).addClass('errors');

            if (!($('#old').hasClass('text-danger'))) {
                $('#old').addClass('text-danger');
            }
            $('#old').removeClass('text-success');

            if (!($('#num-carac').hasClass('text-danger'))) {
                $('#num-carac').addClass('text-danger');
            }
            $('#num-carac').removeClass('text-success');

            if (!($('#repeat-carac').hasClass('text-danger'))) {
                $('#repeat-carac').addClass('text-danger');
            }
            $('#repeat-carac').removeClass('text-success');

            if (!($('#min-carac').hasClass('text-danger'))) {
                    $('#min-carac').addClass('text-danger');
                }
            $('#min-carac').removeClass('text-success');

            if (!($('#spec-carac').hasClass('text-danger'))) {
                    $('#spec-carac').addClass('text-danger');
                }
            $('#spec-carac').removeClass('text-success');

            if (!($('#carac').hasClass('text-danger'))) {
                    $('#carac').addClass('text-danger');
                }
            $('#carac').removeClass('text-success');

            if (!($('#pers-carac').hasClass('text-danger'))) {
                    $('#pers-carac').addClass('text-danger');
                }
            $('#pers-carac').removeClass('text-success');

            if (!($('#confirm').hasClass('text-danger'))) {
                    $('#confirm').addClass('text-danger');
                }
            $('#confirm').removeClass('text-success');
        }
    });

    $(password).on('focus', function () {
        $(password).removeClass('errors');
        $(password).css({'border-color': '#8AB7B6'});
        $('#error-pass').text('');
    });

    $(confirm).keyup( function () {
        if ( $(confirm).val() !== ""){
            if ( $(confirm).val() !== $(password).val()) {
                $('#confirm').removeClass('text-success');
                if ( !($('#confirm').hasClass('text-danger')) ) {
                    $('#confirm').addClass('text-danger');
                }
                $(confirm).addClass('errors');
            }
            else{
                $(confirm).css({border: '2px solid #d2d6de'});
                $(confirm).removeClass('errors');
                $('#confirm').removeClass('text-danger');
                $('#confirm').addClass('text-success');
                $('#error-conf-pass').empty();
            }
        }
        else if ($(confirm).val() === ""){
            $('#error-conf-pass').text(msj);
            $(confirm).addClass('errors');

            if (!($('#confirm').hasClass('text-danger'))) {
                    $('#confirm').addClass('text-danger');
                }
            $('#confirm').removeClass('text-success');
        }
    });

    $(confirm).on('focus', function () {
        $(confirm).removeClass('errors');
        $(confirm).css({'border-color': '#8AB7B6'});
        $('#error-conf-pass').empty();
    });

});


function data_customer(valor) {
    var normalize = (function() {
        var from = "ÃÀÁÄÂÈÉËÊÌÍÏÎÒÓÖÔÙÚÜÛãàáäâèéëêìíïîòóöôùúüûÇç",
            to   = "AAAAAEEEEIIIIOOOOUUUUaaaaaeeeeiiiioooouuuucc",
            mapping = {};

        for(var i = 0, j = from.length; i < j; i++ )
            mapping[ from.charAt( i ) ] = to.charAt( i );

        return function( str ) {
            var ret = [];
            for( var i = 0, j = str.length; i < j; i++ ) {
                var c = str.charAt( i );
                if( mapping.hasOwnProperty( str.charAt( i ) ) )
                    ret.push( mapping[ c ] );
                else
                    ret.push( c );
            }
            return ret.join( '' );
        }

    })();
    var first_name = normalize($("#name_customer").text().toLowerCase()).split(' ');
    var last_name = normalize($("#last-name_customer").text().toLowerCase()).split(' ');
    var ci_cust = $("#ci_customer").text().split('-');
    var phone_home = $("#phone-home").text().split('-');
    var cellphone = $("#cellphone").text().split('-');
    var phone_office = $("#phone-office").text().split('-');
    var birthday = $("#birthday").text();
    var birthday_split = $("#birthday").text().split('-');
    

    return !!((first_name[0].includes(normalize(valor.toLowerCase()))) ||
    (normalize(valor.toLowerCase()).includes(first_name[0])) ||
    (first_name[1].includes(normalize(valor.toLowerCase()))) ||
    (normalize(valor.toLowerCase()).includes(first_name[1])) ||
    (last_name[0].includes(normalize(valor.toLowerCase()))) ||
    (normalize(valor.toLowerCase()).includes(last_name[0])) ||
    (last_name[1].includes(normalize(valor.toLowerCase()))) ||
    (normalize(valor.toLowerCase()).includes(last_name[1])) ||
    (ci_cust[1].includes(valor)) ||
    (valor.includes(ci_cust[1])) ||
    (birthday.includes(valor)) ||
    (valor.includes(birthday)) ||
    (valor.includes(birthday_split[0])) ||
    (birthday_split[0].includes(valor)) ||
    (valor.includes(birthday_split[1])) ||
    (birthday_split[1].includes(valor)) ||
    (valor.includes(birthday_split[2])) ||
    (birthday_split[2].includes(valor)) ||
    (valor.includes(cellphone[0])) ||
    (cellphone[0].includes(valor)) ||
    (valor.includes(cellphone[1])) ||
    (cellphone[1].includes(valor)) ||
    (valor.includes(phone_home[0])) ||
    (phone_home[0].includes(valor)) ||
    (valor.includes(phone_home[1])) ||
    (phone_home[1].includes(valor)) ||
    (valor.includes(phone_office[0])) ||
    (phone_office[0].includes(valor)) ||
    (valor.includes(phone_office[1])) ||
    (phone_office[1].includes(valor)));
}
