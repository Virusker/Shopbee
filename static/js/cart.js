function update_total_cart() {
    var total_all = 0;
    var total_qty = 0;
    var p = 0;
    var q = 0;
    $('[id^=total]').each(function () {
        var id = $(this).attr('id').split('-')[1];
        if (id != null) {
            p = parseInt( $('#total-' + id).html().replace('₫','').replaceAll('.','') , 10);
            if (!isNaN(p))
                total_all += p;

            q = parseInt($('#quantity-' + id).val(), 10);
            if (!isNaN(q))
                total_qty += q;
        }
    });
    total_all = total_all.toLocaleString('vi', {
        style: 'currency',
        currency: 'VND'
    });
    $('#all-total').html(total_all);
    $('#total_quantity_cart').html(total_qty);
}
