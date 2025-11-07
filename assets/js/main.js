document.addEventListener('DOMContentLoaded', () => {
  const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const shouldReduceMotion = reduceMotionQuery.matches;

  const instagramCard = document.querySelector('[data-instagram-state]');
  if (instagramCard) {
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
  }

  const heroPhrase = document.querySelector('[data-hero-phrase]');
  const heroPhrases = ['町家のぬくもり', '旬の味わい', 'ほっとする時間'];
  if (heroPhrase) {
    let phraseIndex = 0;
    const swapPhrase = () => {
      phraseIndex = (phraseIndex + 1) % heroPhrases.length;
      heroPhrase.classList.add('is-swapping');
      window.setTimeout(() => {
        heroPhrase.textContent = heroPhrases[phraseIndex];
        heroPhrase.classList.remove('is-swapping');
      }, 200);
    };

    if (!shouldReduceMotion && heroPhrases.length > 1) {
      window.setInterval(swapPhrase, 3800);
    } else {
      heroPhrase.textContent = heroPhrases[0];
    }
  }

  const animateElements = document.querySelectorAll('[data-animate]');
  if (animateElements.length) {
    if (shouldReduceMotion || !('IntersectionObserver' in window)) {
      animateElements.forEach((element) => {
        element.classList.add('is-visible');
      });
    } else {
      const observer = new IntersectionObserver(
        (entries, obs) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('is-visible');
              obs.unobserve(entry.target);
            }
          });
        },
        {
          threshold: 0.2,
          rootMargin: '0px 0px -80px',
        }
      );

      animateElements.forEach((element) => {
        if (element.dataset.animate === 'hero') {
          window.requestAnimationFrame(() => {
            element.classList.add('is-visible');
          });
        } else {
          observer.observe(element);
        }
      });
    }
  }

  const heroSection = document.querySelector('.hero');
  if (heroSection && !shouldReduceMotion) {
    const updateParallax = () => {
      const offset = Math.max(-40, window.scrollY * -0.08);
      heroSection.style.setProperty('--hero-parallax', `${offset}px`);
    };

    updateParallax();
    window.addEventListener('scroll', updateParallax, { passive: true });
    window.addEventListener('resize', updateParallax);
  }
});
