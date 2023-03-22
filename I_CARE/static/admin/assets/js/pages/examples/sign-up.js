$(function () {
    $('#sign_up').validate({
        rules: {
            'terms': {
                required: true
            },
            'password2': {
                equalTo: '[name="password1"]'
            }
        },
        highlight: function (input) {
            
            $(input).parents('.form-line').addClass('error');
        },
        unhighlight: function (input) {
            $(input).parents('.form-line').removeClass('error');
        },
        errorPlacement: function (error, element) {
            $(element).parents('.input-group').append(error);
            $(element).parents('.form-group').append(error);
        }
    });
});