document.addEventListener('DOMContentLoaded', () => {
  const instagramCard = document.querySelector('[data-instagram-state]');
  if (!instagramCard) return;

  const state = instagramCard.getAttribute('data-instagram-state');
  const button = instagramCard.querySelector('a.button');
  const caption = instagramCard.querySelector('[data-instagram-caption]');

  if (state === 'available' && button) {
    button.classList.remove('secondary');
    button.setAttribute('href', button.dataset.href);
    button.removeAttribute('aria-disabled');
    button.textContent = 'Instagramをみる';
    if (caption) {
      caption.textContent = '旬の一皿や季節の便りをお届けしています。';
    }
  } else if (button) {
    button.classList.add('secondary');
    button.setAttribute('href', '#');
    button.setAttribute('aria-disabled', 'true');
    button.addEventListener('click', (event) => event.preventDefault());
    button.textContent = 'Instagram準備中';
    if (caption) {
      caption.textContent = '公式アカウントは準備中です。公開までしばらくお待ちください。';
    }
  }
});
