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

  const heroSparkles = document.querySelector('.hero-sparkles');
  if (heroSparkles && !shouldReduceMotion) {
    const createSparkle = () => {
      const sparkle = document.createElement('span');
      sparkle.style.left = `${Math.random() * 100}%`;
      sparkle.style.top = `${Math.random() * 100}%`;
      const duration = 3.5 + Math.random() * 3.5;
      sparkle.style.animationDuration = `${duration}s`;
      sparkle.style.animationDelay = `${Math.random() * -duration}s`;
      sparkle.addEventListener('animationiteration', () => {
        sparkle.style.left = `${Math.random() * 100}%`;
        sparkle.style.top = `${Math.random() * 100}%`;
      });
      heroSparkles.appendChild(sparkle);
    };

    const sparkleCount = 14;
    for (let i = 0; i < sparkleCount; i += 1) {
      createSparkle();
    }
  }

  const heroCharacters = document.querySelector('.hero-characters');
  if (heroCharacters && !shouldReduceMotion) {
    const handlePointer = (event) => {
      const bounds = heroCharacters.getBoundingClientRect();
      const offsetX = (event.clientX - bounds.left) / bounds.width - 0.5;
      const offsetY = (event.clientY - bounds.top) / bounds.height - 0.5;
      heroCharacters.style.setProperty('--tilt-x', (offsetY * -8).toFixed(2));
      heroCharacters.style.setProperty('--tilt-y', (offsetX * 8).toFixed(2));
    };

    const resetTilt = () => {
      heroCharacters.style.setProperty('--tilt-x', '0');
      heroCharacters.style.setProperty('--tilt-y', '0');
    };

    heroCharacters.addEventListener('pointermove', handlePointer);
    heroCharacters.addEventListener('pointerleave', resetTilt);
    resetTilt();
  }
});
