/* bento.js */
document.addEventListener("DOMContentLoaded", () => {
  // Number counter animation for stats
  const counters = document.querySelectorAll('.bento-stat-num span');
  const speed = 50; 

  const animateCounters = () => {
    counters.forEach(counter => {
      const updateCount = () => {
        const target = +counter.getAttribute('data-target');
        const count = +counter.innerText;
        const inc = target / speed;

        if (count < target) {
          counter.innerText = Math.ceil(count + inc);
          setTimeout(updateCount, 20);
        } else {
          counter.innerText = target;
        }
      };
      // only animate if data-target is valid number
      if(counter.getAttribute('data-target')) {
         updateCount();
      }
    });
  }

  // Intersection Observer to trigger counter when in view
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting) {
        animateCounters();
        observer.disconnect();
      }
    });
  }, { threshold: 0.1 });

  const statSection = document.querySelector('.bento-stat-num');
  if(statSection) {
    observer.observe(statSection);
  }

  // Lightweight 3D tilt effect for bento items
  const items = document.querySelectorAll('.bento-item');
  items.forEach(item => {
    item.addEventListener('mousemove', e => {
      const rect = item.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const xPct = x / rect.width - 0.5;
      const yPct = y / rect.height - 0.5;

      item.style.transform = `perspective(1000px) rotateX(${yPct * -10}deg) rotateY(${xPct * 10}deg) translateY(-5px) scale(1.02)`;
    });

    item.addEventListener('mouseleave', () => {
      item.style.transform = `perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)`;
    });
  });
});
