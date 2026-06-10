(function () {
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setupCanvas() {
    var canvas = document.getElementById("ambient-canvas");
    if (!canvas || reducedMotion) {
      return;
    }

    var ctx = canvas.getContext("2d");
    var width = 0;
    var height = 0;
    var rafId = 0;
    var streams = [];
    var particles = [];
    var glyphs = "0123456789ABCDEF<>[]{}#/|";

    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;

      var count = Math.max(32, Math.floor(width / 20));
      streams = [];
      for (var i = 0; i < count; i += 1) {
        streams.push({
          x: i * (width / count),
          y: Math.random() * -height,
          speed: 2 + Math.random() * 3.2,
          alpha: 0.2 + Math.random() * 0.3,
          isHot: Math.random() < 0.18,
        });
      }

      particles = [];
      for (var p = 0; p < 42; p += 1) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.28,
          vy: (Math.random() - 0.5) * 0.28,
          r: 0.8 + Math.random() * 1.8,
          a: 0.08 + Math.random() * 0.12,
        });
      }
    }

    function drawRain() {
      ctx.font = "13px JetBrains Mono, monospace";
      for (var i = 0; i < streams.length; i += 1) {
        var s = streams[i];
        var text = glyphs[Math.floor(Math.random() * glyphs.length)];
        if (s.isHot) {
          ctx.fillStyle = "rgba(239,68,68," + s.alpha + ")";
        } else {
          ctx.fillStyle = "rgba(59,130,246," + s.alpha + ")";
        }
        ctx.fillText(text, s.x, s.y);
        s.y += s.speed;
        if (s.y > height + 20) {
          s.y = -30 - Math.random() * (height * 0.45);
          s.isHot = Math.random() < 0.18;
        }
      }
    }

    function drawParticles() {
      for (var i = 0; i < particles.length; i += 1) {
        var p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) { p.x = width; }
        if (p.x > width) { p.x = 0; }
        if (p.y < 0) { p.y = height; }
        if (p.y > height) { p.y = 0; }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(96,165,250," + p.a + ")";
        ctx.fill();
      }
    }

    function frame() {
      ctx.fillStyle = "rgba(2,2,5,0.24)";
      ctx.fillRect(0, 0, width, height);
      drawRain();
      drawParticles();
      rafId = window.requestAnimationFrame(frame);
    }

    resize();
    frame();

    window.addEventListener("resize", resize);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) {
        window.cancelAnimationFrame(rafId);
      } else {
        frame();
      }
    });
  }

  function setupReveal() {
    if (typeof ScrollReveal === "undefined" || reducedMotion) {
      return;
    }
    ScrollReveal().reveal(".reveal", {
      distance: "28px",
      origin: "bottom",
      opacity: 0,
      duration: 680,
      easing: "cubic-bezier(0.22, 0.68, 0.27, 1)",
      interval: 70,
      cleanup: true,
    });
  }

  function setupFaqAccordion() {
    document.querySelectorAll(".faq-question").forEach(function (button) {
      button.addEventListener("click", function () {
        var item = button.closest(".faq-item");
        var alreadyOpen = item.classList.contains("open");
        document.querySelectorAll(".faq-item.open").forEach(function (openItem) {
          openItem.classList.remove("open");
          var openBtn = openItem.querySelector(".faq-question");
          if (openBtn) {
            openBtn.setAttribute("aria-expanded", "false");
          }
        });
        if (!alreadyOpen) {
          item.classList.add("open");
          button.setAttribute("aria-expanded", "true");
        }
      });
    });
  }

  function setupFlashDismiss() {
    document.querySelectorAll(".flash-message").forEach(function (message) {
      window.setTimeout(function () {
        message.style.opacity = "0";
        message.style.transform = "translateX(10px)";
        message.style.transition = "all 220ms ease";
        window.setTimeout(function () { message.remove(); }, 240);
      }, 4200);
    });
  }

  function hydrateIcons() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      try {
        window.lucide.createIcons();
      } catch (error) {
        console.error("Lucide render failed", error);
      }
    }
  }

  setupCanvas();
  setupReveal();
  setupFaqAccordion();
  setupFlashDismiss();
  hydrateIcons();
})();
