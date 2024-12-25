$(document).ready(function () {
    $('a[href^="#"]').on('click', function (event) {
        event.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top
            }, 1000);
        }
    });

    $('#home-link').on('click', function () {
        $('html, body').animate({ scrollTop: $('.page_title').offset().top }, 1000);
    });

    $('#members_link').on('click', function () {
        $('html, body').animate({ scrollTop: $('.members').offset().top }, 1000);
    });

    $('#contact_link').on('click', function () {
        $('html, body').animate({ scrollTop: $('.contact').offset().top }, 1000);
    });

});

new Splide('#image-carousel1').mount();

var splide1 = new Splide('#image-carousel1', {
    perPage: 3,
    perMove: 1,
    cover: boolean = false,
    gap: '3rem',
    autoHeight: boolean = true,
    cloneStatus: boolean = true,
    drag: boolean = true,
    clones: 2,
    classes: {
        pagination: 'splide__pagination your-class-pagination',
        page: 'splide__pagination__page your-class-page',
    },
});

splide1.mount();