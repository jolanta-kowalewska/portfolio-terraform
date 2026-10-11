const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, i) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, i * 100);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.fade-in, .timeline-item').forEach(el => {
            observer.observe(el);
        });
