/**
 * Created by Cinthya C. Ramos G. on 16/6/2017.
*/

$(document).ready(function (){
    drop_trans_tdc();

    $('#datepicker').val('');

    $('#datepicker2').val('');

});

function drop_tdc(tdc){
    var path = window.location.pathname.split('/');
    var key = path[3];
    $("#tdc_drop").empty();

    $.each(tdc,function (i,val) {
        var d = val[3].split('-');
        var last_date = d[2][0]+d[2][1] + '/' + d[1] + '/' + d[0];
        d = val[8].split('-');
        var date = d[2][0]+d[2][1] + '/' + d[1] + '/' + d[0];
        if (key === '1' && val[0].includes("VISA")) {
            $("#tdc_drop").append('<option value="'+(i+1)+'" selected> '+val[0]+'  '+val[1].substring(8)+'</option>');
            $("#status").text(val[2]);
            $("#last-date-payment").text(last_date);
            $('#amount-payment').text( 'Bs. ' +val[4]);
            $('#balance').text( 'Bs. ' +val[5]);
            $('#available').text( 'Bs. ' +val[6]);
            $('#min-payment').text( 'Bs. ' +val[7]);
            $('#date-payment').text(date);
            $('#limit').text( 'Bs. ' +val[9]);
        }
        else if (key === '2' && val[0].includes("MASTERCARD")) {
            $("#tdc_drop").append('<option value="'+(i+1)+'" selected> '+val[0]+'  '+val[1].substring(8)+'</option>');
            $("#status").text(val[2]);
            $("#last-date-payment").text(last_date);
            $('#amount-payment').text( 'Bs. ' +val[4]);
            $('#balance').text( 'Bs. ' +val[5]);
            $('#available').text( 'Bs. ' +val[6]);
            $('#min-payment').text( 'Bs. ' +val[7]);
            $('#date-payment').text(date);
            $('#limit').text( 'Bs. ' +val[9]);
        }
        else if (key === '3' && val[0].includes("AMERICAN")) {
            $("#tdc_drop").append('<option value="'+(i+1)+'" selected> '+val[0]+'  '+val[1].substring(8)+'</option>');
            $("#status").text(val[2]);
            $("#last-date-payment").text(last_date);
            $('#amount-payment').text( 'Bs. ' +val[4]);
            $('#balance').text( 'Bs. ' +val[5]);
            $('#available').text( 'Bs. ' +val[6]);
            $('#min-payment').text( 'Bs. ' +val[7]);
            $('#date-payment').text(date);
            $('#limit').text( 'Bs. ' +val[9]);
        }
        else {
            $("#tdc_drop").append('<option value="'+(i+1)+'"> '+val[0]+'  '+val[1].substring(8)+'</option>');
        }
    })

}

function movement_table_tdc(movements) {
    var path = window.location.pathname.split('/');
    var key = path[3];
    var j;

    if (key === '1') {
        j = 0;
    }
    else if (key === '2') {
        j = 1;
    }
    else {
        j = 2;
    }

    $('#example').DataTable().destroy();
    $("#mov-table-tdc").empty();

    var mov = movements[j];
    $.each(mov, function (i, val) {
        var d = val[0].split('-');
        var date = d[2][0]+d[2][1] + '/' + d[1] + '/' + d[0];
        $("#mov-table-tdc").append('<tr><td>' + date + '</td>' +
            '<td> ' + val[1] + '</td>' +
            '<td class="text-bold">' + 'Bs. ' + val[2] + '</td>' +
            '</tr>')
    });

    DatatablesExec();

}

function drop_trans_tdc(){
    var type_trans = ['Pagos', 'POS'];
    $("#trans").append('<option value="'+'0'+'"" selected="selected"> '+"Todas"+'</option>');

    $.each(type_trans,function (i,val) {
           $("#trans").append('<option value="'+val+'"> '+val+'</option>');
    })
}

function DatatablesExec() {
    var table = $('#example').DataTable({
        "paging": true,
        "lengthChange": false,
        "destroy": true,
        "ordering": false,
        "info": true,
        "autoWidth": true,
        "pageLength":5,
        "language": {
            "emptyTable": "No tiene movimientos en esta tarjeta en el mes actual"
        },
        dom:'lr<"table-filter-container">tip',
        initComplete: function () {
            $('#btn-con').click(function () {
                if ($('#trans').val() !== 0) {
                    if ($('#datepicker').val() === '' && $($('#datepicker2').val() === '')) {
                        table.search($('#trans').val()).draw();
                    }
                }
            });
        }
    });

    $("#example_paginate").addClass("pull-right");
    $("#example_paginate").css({height: '60px'});
}

function download_movement_tdc(a) {
    var path = window.location.href.split('/');
    var url_api = path[0]+"/"+path[1]+"/"+"localhost:8001"+"/ajax/data-customer/";
    var o;
    var s = $('#datepicker').val();
    var e = $('#datepicker2').val();
    var select = $('#trans').val();

    if (validate_date(s,e)) {
        var today = new Date();
        var start = s;
        var end = e;
        if (s === '') {
            start = 1 + '/' + (today.getMonth()+1) + '/' + today.getFullYear();
        }
        if (e === '') {
            end = today.getDate() + '/' + (today.getMonth()+1) + '/' + today.getFullYear();
        }

        $.ajax({
            url: url_api,
            origin: 'localhost:8000',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            data: {
                num: a,
                start: start,
                end: end,
                select: select,
                option: path[4]
            },
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data.product) {
                    var mov;
                    if (path[5] === '1') {
                        mov = data.mov_tdc[0];
                    }
                    else if (path[5] === '2'){
                        mov = data.mov_tdc[1];
                    }
                    else{
                        mov = data.mov_tdc[2]
                    }
                    var tdc = document.getElementById('tdc_drop').options[document.getElementById('tdc_drop').selectedIndex].text;
                    $('#my_form_data').val(JSON.stringify([mov,start,end,select,tdc]));
                    $('#my_form').submit();
                }
            },
            error: function (data) {
                alert("Lo sentimos, hay problemas con el servidor. Intente más tarde.");
                // move('logout');
            }
        });
    }
    else if (!(validate_date(s,e))) {
        $('#datepicker2').addClass('errors');
        var msg = 'La fecha final para la consulta de movimientos no ' +
            'puede ser mayor a la fecha de inicio.';
        notification_error(msg);
    }
}
