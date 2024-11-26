jQuery(function ($) {
    $(document).ready(function () {
        select();
        callmodal();
        gallery();
        tabs();
        clock();
    })
})


// setSelect
function select() {
    $('.js-example-basic-single').select2({
        width: '100%',
    });
}

// callmodal
function callmodal() {
    $('.callmodal').click(function(){
        var idPopup = $(this).data('id')
            $.fancybox.open({
            src: idPopup,
            type: 'inline'
        });
    });
}

// gallery
function gallery() {
    $("a#single_image").fancybox();
}

function tabs() {
    var tab = $('#tabs .tabs-items > div'); 
    tab.hide().filter(':first').show(); 
    
    // Клики по вкладкам.
    $('#tabs .tabs-nav a').click(function(){
        tab.hide(); 
        tab.filter(this.hash).show(); 
        $('#tabs .tabs-nav a').removeClass('active');
        $(this).addClass('active');
        return false;
    }).filter(':first').click();
};

function clock() {
    var date = new Date(new Date().valueOf() + 12 * 24 * 60 * 60 * 1000);
    $('.getting-started').countdown(date, function(event) {
       $(this).html(event.strftime('<div class="counter__item"><div class="counter__item"><span>%H</span></div><div class="counter__colon">:</div><div class="counter__item"><span>%M</span></div><div class="counter__colon">:</div><div class="counter__item"><span>%S</span></div>'));
     });
};

let fields = document.querySelectorAll('.field__file');
Array.prototype.forEach.call(fields, function (input) {
    let label = input.nextElementSibling,
    labelVal = label.querySelector('.field__file-fake').innerText;

    input.addEventListener('change', function (e) {
    let countFiles = '';
    if (this.files && this.files.length >= 1)
        countFiles = this.files.length;

    if (countFiles)
        label.querySelector('.field__file-fake').innerText = 'Выбрано файлов: ' + countFiles;
    else
        label.querySelector('.field__file-fake').innerText = labelVal;
    });
});


$('.messages__box').click(function(event) {
    $(this).toggleClass('active');
});