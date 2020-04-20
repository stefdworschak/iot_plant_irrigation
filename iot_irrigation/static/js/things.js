$(document).ready(function(){

    $('#add_thing').submit(function(event){
        $('.error-output').hide()
        const regex = new RegExp('^[a-zA-Z0-9:_-]+$');
        let thing_name = $('input[name="thing_name"]').val()
        console.log(thing_name)
        if(!regex.test(thing_name)){
            event.preventDefault();
            $('.error-output').text('Thing names can only contain the following letters: a-zA-Z0-9:_-')
            $('.error-output').show()
            $('.error-output').css('display', 'block')
        }
    })

})