(function () {
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setupBeaztIntro() {
    var intro = document.querySelector(".beazt-intro");
    var headline = document.querySelector(".t-display");
    if (!intro || reducedMotion) {
      return;
    }

    intro.classList.add("is-live");
    if (headline) {
      headline.style.opacity = "0";
      headline.style.transform = "translateY(10px)";
      headline.style.transition = "opacity 520ms ease, transform 520ms ease";
      window.setTimeout(function () {
        headline.style.opacity = "1";
        headline.style.transform = "translateY(0)";
      }, 520);
    }
  }

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
    var glyphs = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ<>/=+-*";

    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;

      var count = Math.max(24, Math.floor(width / 21));
      streams = [];
      for (var i = 0; i < count; i += 1) {
        streams.push({
          x: i * (width / count),
          y: Math.random() * -height,
          speed: 1.8 + Math.random() * 2.9,
          alpha: 0.14 + Math.random() * 0.25,
        });
      }

      particles = [];
      for (var p = 0; p < 46; p += 1) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.35,
          vy: (Math.random() - 0.5) * 0.35,
          r: 1 + Math.random() * 2,
          a: 0.14 + Math.random() * 0.16,
        });
      }
    }

    function drawRain() {
      ctx.font = "13px Inter, sans-serif";
      for (var i = 0; i < streams.length; i += 1) {
        var s = streams[i];
        var text = glyphs[Math.floor(Math.random() * glyphs.length)];
        ctx.fillStyle = "rgba(118,171,255," + s.alpha + ")";
        ctx.fillText(text, s.x, s.y);
        s.y += s.speed;
        if (s.y > height + 20) {
          s.y = -30 - Math.random() * (height * 0.36);
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
        ctx.fillStyle = "rgba(137,190,255," + p.a + ")";
        ctx.fill();
      }
    }

    function frame() {
      ctx.fillStyle = "rgba(3,7,24,0.24)";
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
      easing: "cubic-bezier(0.17, 0.84, 0.44, 1)",
      interval: 55,
      cleanup: true,
    });
  }

  function setupTypewriter() {
    if (reducedMotion) {
      return;
    }
    var nodes = document.querySelectorAll("[data-typewriter]");
    nodes.forEach(function (node) {
      var target = node.getAttribute("data-typewriter");
      if (!target) {
        return;
      }

      var original = node.innerHTML;
      var remainder = original.replace(/^.*?<br>/i, "");
      var index = 0;
      node.innerHTML = "&nbsp;<br>" + remainder;

      var timer = window.setInterval(function () {
        index += 1;
        node.innerHTML = target.slice(0, index) + "<span aria-hidden='true'>_</span><br>" + remainder;
        if (index >= target.length) {
          window.clearInterval(timer);
          node.innerHTML = target + "<br>" + remainder;
        }
      }, 44);
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

  function setupCounter() {
    var nodes = document.querySelectorAll(".stat-value");
    if (!nodes.length || typeof IntersectionObserver === "undefined" || reducedMotion) {
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) {
          return;
        }

        var el = entry.target;
        var text = el.textContent.trim();
        var match = text.match(/\d+/);
        if (!match) {
          observer.unobserve(el);
          return;
        }

        var target = parseInt(match[0], 10);
        var prefix = text.slice(0, match.index);
        var suffix = text.slice(match.index + match[0].length);
        var value = 0;
        var steps = 32;
        var increment = target / steps;
        var timer = window.setInterval(function () {
          value += increment;
          if (value >= target) {
            el.textContent = prefix + target + suffix;
            window.clearInterval(timer);
          } else {
            el.textContent = prefix + Math.floor(value) + suffix;
          }
        }, 28);

        observer.unobserve(el);
      });
    }, { threshold: 0.4 });

    nodes.forEach(function (el) { observer.observe(el); });
  }

  setupBeaztIntro();
  setupCanvas();
  setupReveal();
  setupTypewriter();
  setupFaqAccordion();
  setupFlashDismiss();
  setupCounter();
})();
