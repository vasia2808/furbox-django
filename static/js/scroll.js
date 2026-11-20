document.querySelectorAll('.product-list').forEach(list => {
    const cards = list.querySelector('.product-list-cards');
    const left = list.querySelector('.scroll-left');
    const right = list.querySelector('.scroll-right');

    const gap = parseInt(window.getComputedStyle(cards).gap, 10);
    const scrollWidth = cards.clientWidth + gap;

    left.addEventListener('click', () => {
        cards.scrollBy({
            left: -scrollWidth,
            behavior: 'smooth'
        });
    });

    right.addEventListener('click', () => {
        cards.scrollBy({
            left: scrollWidth,
            behavior: 'smooth'
        });
    });
});