$(function() {
    // //Textarea auto growth
    // autosize($('textarea.auto-growth'));

    // //Datetimepicker plugin
    // $('.datetimepicker').bootstrapMaterialDatePicker({
    //     format: 'dddd DD MMMM YYYY - HH:mm',
    //     clearButton: true,
    //     weekStart: 1
    // });

    // $('.datepicker').bootstrapMaterialDatePicker({
    //     format: 'dddd DD MMMM YYYY',
    //     clearButton: true,
    //     weekStart: 1,
    //     time: false
    // });

    // $('.timepicker').bootstrapMaterialDatePicker({
    //     format: 'HH:mm',
    //     clearButton: true,
    //     date: false
    // });

    //Bootstrap datepicker plugin
 
    $('.Date input').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        container: '.Date'
    });
     

    $('#bs_datepicker_range_container').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        container: '#bs_datepicker_range_container',
    });
    
    $('#inventory_container').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        container: '#inventory_container',
    });

    $('#inventory_sales_container').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        container: '#inventory_sales_container',
    });
     
    
});