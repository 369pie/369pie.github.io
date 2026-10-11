(function () {
  var prefersReduced =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav-menu");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var path = window.location.pathname.replace(/\/$/, "") || "/";
  if (nav) {
    var links = nav.querySelectorAll("a[href]");
    links.forEach(function (link) {
      var href = link.getAttribute("href").replace(/\/$/, "") || "/";
      if (href === path || (href !== "/" && path.indexOf(href) === 0)) {
        link.classList.add("current");
      }
    });
  }

  var header = document.getElementById("header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 12);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  if (!prefersReduced && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll(
      ".site-hero, #main .post, #sidebar .widget, .resume-page .resume-block"
    );
    targets.forEach(function (el) {
      el.classList.add("pf-reveal");
    });
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -6% 0px", threshold: 0.08 }
    );
    targets.forEach(function (el) {
      io.observe(el);
    });
  } else {
    document.querySelectorAll(".pf-reveal").forEach(function (el) {
      el.classList.add("is-visible");
    });
  }
})();
