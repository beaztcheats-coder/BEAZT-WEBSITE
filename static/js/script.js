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

  function setupFormValidation() {
    var forms = document.querySelectorAll("form[novalidate]");
    if (!forms.length) { return; }

    var validationRules = {
      email: function(value) {
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value) ? "" : "Please enter a valid email address";
      },
      password: function(value) {
        if (!value) return "Password is required";
        if (value.length < 8) return "Password must be at least 8 characters";
        return "";
      },
      username: function(value) {
        if (!value) return "Username is required";
        if (value.length < 3) return "Username must be at least 3 characters";
        return "";
      },
      confirm_password: function(value) {
        var passwordInput = document.querySelector('input[name="password"]');
        if (!passwordInput) return "";
        if (value !== passwordInput.value) return "Passwords do not match";
        return "";
      }
    };

    function showError(input, message) {
      var group = input.closest(".form-group");
      if (!group) return;
      
      group.classList.add("has-error");
      group.classList.remove("has-success");
      input.classList.add("is-error");
      input.classList.remove("is-success");
      input.setAttribute("aria-invalid", "true");
      
      var existingError = group.querySelector(".form-error");
      if (existingError) { existingError.remove(); }
      
      if (message) {
        var errorDiv = document.createElement("div");
        errorDiv.className = "form-error";
        errorDiv.setAttribute("role", "alert");
        errorDiv.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
        errorDiv.appendChild(document.createTextNode(message));
        group.appendChild(errorDiv);
      }
    }

    function showSuccess(input) {
      var group = input.closest(".form-group");
      if (!group) return;
      
      group.classList.remove("has-error");
      group.classList.add("has-success");
      input.classList.remove("is-error");
      input.classList.add("is-success");
      input.setAttribute("aria-invalid", "false");
      
      var existingError = group.querySelector(".form-error");
      if (existingError) { existingError.remove(); }
    }

    function clearValidation(input) {
      var group = input.closest(".form-group");
      if (!group) return;
      
      group.classList.remove("has-error", "has-success");
      input.classList.remove("is-error", "is-success");
      input.removeAttribute("aria-invalid");
      
      var existingError = group.querySelector(".form-error");
      if (existingError) { existingError.remove(); }
    }

    function validateField(input) {
      var value = input.value.trim();
      var type = input.type;
      var name = input.name;
      var required = input.hasAttribute("required");
      var minlength = parseInt(input.getAttribute("minlength"), 10);

      if (required && !value) {
        var label = input.closest(".form-group").querySelector(".form-label");
        var fieldName = label ? label.textContent.trim().replace(/[^\w\s]/gi, "").trim() : name;
        showError(input, fieldName + " is required");
        return false;
      }

      if (type === "email" && value) {
        var error = validationRules.email(value);
        if (error) { showError(input, error); return false; }
      }

      if (name === "password" && value) {
        var error = validationRules.password(value);
        if (error) { showError(input, error); return false; }
      }

      if (name === "confirm_password" && value) {
        var error = validationRules.confirm_password(value);
        if (error) { showError(input, error); return false; }
      }

      if (minlength && value && value.length < minlength) {
        showError(input, "Must be at least " + minlength + " characters");
        return false;
      }

      if (value) {
        showSuccess(input);
      } else {
        clearValidation(input);
      }
      
      return true;
    }

    forms.forEach(function(form) {
      var inputs = form.querySelectorAll("input:not([type='submit']):not([type='button']):not([type='checkbox']):not([type='radio'])");
      
      inputs.forEach(function(input) {
        input.addEventListener("blur", function() {
          if (input.value.trim() || input.hasAttribute("required")) {
            validateField(input);
          }
        });
        
        input.addEventListener("input", function() {
          if (input.classList.contains("is-error") || input.classList.contains("is-success")) {
            if (input.classList.contains("is-error")) {
              validateField(input);
            }
          }
        });
      });

      form.addEventListener("submit", function(e) {
        var isValid = true;
        var firstError = null;
        
        inputs.forEach(function(input) {
          if (!validateField(input)) {
            isValid = false;
            if (!firstError) {
              firstError = input;
            }
          }
        });

        var checkboxRequired = form.querySelector("input[type='checkbox'][required]");
        if (checkboxRequired && !checkboxRequired.checked) {
          isValid = false;
          var checkboxGroup = checkboxRequired.closest(".form-group") || checkboxRequired.closest(".form-checkbox");
          if (checkboxGroup) {
            checkboxGroup.classList.add("has-error");
          }
        }

        if (!isValid) {
          e.preventDefault();
          if (firstError) {
            firstError.focus();
          }
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

  function setupFooterReveal() {
    var footer = document.querySelector(".footer");
    if (!footer || reducedMotion) { return; }
    
    if (!("IntersectionObserver" in window)) {
      footer.classList.add("footer-visible");
      return;
    }
    
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          footer.classList.add("footer-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    io.observe(footer);
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
  setupFormValidation();
  setupFlashDismiss();
  setupCounters();
  setupMobileBuyBar();
  setupFooterReveal();
  hydrateIcons();
})();
