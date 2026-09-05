(function () {
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia("(max-width: 900px)").matches;
  var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  var saveData = conn && (conn.saveData || conn.effectiveType === "2g" || conn.effectiveType === "slow-2g");

  /* ── Header scroll effect ─────────────────────────────── */
  function setupHeaderScroll() {
    var navbar = document.querySelector(".navbar");
    if (!navbar) { return; }
    
    var scrollThreshold = 20;
    var ticking = false;
    
    function updateNavbar() {
      if (window.scrollY > scrollThreshold) {
        navbar.classList.add("scrolled");
      } else {
        navbar.classList.remove("scrolled");
      }
      ticking = false;
    }
    
    window.addEventListener("scroll", function () {
      if (!ticking) {
        window.requestAnimationFrame(updateNavbar);
        ticking = true;
      }
    }, { passive: true });
    
    updateNavbar();
  }

  /* ── Premium mobile menu ──────────────────────────────── */
  function setupMobileMenu() {
    var burger = document.querySelector(".nav-burger");
    var overlay = document.querySelector(".mobile-menu-overlay");
    var menu = document.querySelector(".mobile-menu");
    
    if (!burger || !menu) { return; }
    
    function openMenu() {
      burger.classList.add("is-active");
      burger.setAttribute("aria-expanded", "true");
      if (overlay) {
        overlay.classList.add("is-visible");
      }
      menu.classList.add("is-open");
      document.body.style.overflow = "hidden";
    }
    
    function closeMenu() {
      burger.classList.remove("is-active");
      burger.setAttribute("aria-expanded", "false");
      if (overlay) {
        overlay.classList.remove("is-visible");
      }
      menu.classList.remove("is-open");
      document.body.style.overflow = "";
    }
    
    burger.addEventListener("click", function () {
      var isOpen = menu.classList.contains("is-open");
      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    });
    
    if (overlay) {
      overlay.addEventListener("click", closeMenu);
    }
    
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("is-open")) {
        closeMenu();
        burger.focus();
      }
    });
    
    var menuLinks = menu.querySelectorAll(".nav-link");
    menuLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        closeMenu();
      });
    });
  }

  function setupCanvas() {
    var canvas = document.getElementById("ambient-canvas");
    if (!canvas || reducedMotion || isMobile || saveData) {
      if (canvas) { canvas.style.display = "none"; }
      return;
    }

    var ctx = canvas.getContext("2d");
    var width = 0;
    var height = 0;
    var rafId = 0;
    var streams = [];
    var glyphs = "0123456789ABCDEF<>[]{}#/|";

    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;

      var count = Math.max(20, Math.floor(width / 26));
      streams = [];
      for (var i = 0; i < count; i += 1) {
        streams.push({
          x: i * (width / count),
          y: Math.random() * -height,
          speed: 1.6 + Math.random() * 2.6,
          alpha: 0.12 + Math.random() * 0.22,
          isHot: Math.random() < 0.14,
        });
      }
    }

    function drawRain() {
      ctx.font = "13px JetBrains Mono, monospace";
      for (var i = 0; i < streams.length; i += 1) {
        var s = streams[i];
        var text = glyphs[Math.floor(Math.random() * glyphs.length)];
        if (s.isHot) {
          ctx.fillStyle = "rgba(34,211,238," + s.alpha + ")";
        } else {
          ctx.fillStyle = "rgba(30,144,255," + s.alpha + ")";
        }
        ctx.fillText(text, s.x, s.y);
        s.y += s.speed;
        if (s.y > height + 20) {
          s.y = -30 - Math.random() * (height * 0.45);
          s.isHot = Math.random() < 0.14;
        }
      }
    }

    function frame() {
      ctx.fillStyle = "rgba(3,3,5,0.22)";
      ctx.fillRect(0, 0, width, height);
      drawRain();
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
      duration: 640,
      easing: "cubic-bezier(0.22, 0.68, 0.27, 1)",
      interval: 60,
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
          if (openBtn) { openBtn.setAttribute("aria-expanded", "false"); }
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

  function setupCounters() {
    var els = document.querySelectorAll("[data-count]");
    if (!els.length) { return; }

    function animate(el) {
      var target = parseFloat(el.getAttribute("data-count"));
      var suffix = el.getAttribute("data-suffix") || "";
      var isFloat = target % 1 !== 0;
      if (reducedMotion) {
        el.textContent = (isFloat ? target.toFixed(1) : Math.round(target).toLocaleString()) + suffix;
        return;
      }
      var dur = 1400;
      var start = performance.now();
      function step(now) {
        var p = Math.min((now - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        var val = target * eased;
        el.textContent = (isFloat ? val.toFixed(1) : Math.round(val).toLocaleString()) + suffix;
        if (p < 1) { requestAnimationFrame(step); }
      }
      requestAnimationFrame(step);
    }

    if (!("IntersectionObserver" in window)) {
      els.forEach(animate);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animate(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    els.forEach(function (el) { io.observe(el); });
  }

  function setupMobileBuyBar() {
    var bar = document.querySelector(".mobile-buy-bar");
    if (!bar) { return; }
    document.body.classList.add("has-mobile-buy-bar");
  }

  function hydrateIcons() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      try { window.lucide.createIcons(); } catch (error) { console.error("Lucide render failed", error); }
    }
  }

  setupHeaderScroll();
  setupMobileMenu();
  setupCanvas();
  setupReveal();
  setupFaqAccordion();
  setupFlashDismiss();
  setupCounters();
  setupMobileBuyBar();
  hydrateIcons();
})();
