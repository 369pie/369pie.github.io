(function () {
  var prefersReduced =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav-menu");
  function setNavOpen(open) {
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setNavOpen(!nav.classList.contains("is-open"));
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setNavOpen(false);
      });
    });

    document.addEventListener("click", function (e) {
      if (!nav.classList.contains("is-open")) return;
      if (nav.contains(e.target) || toggle.contains(e.target)) return;
      setNavOpen(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setNavOpen(false);
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

  document
    .querySelectorAll(".post-content table, .resume-block table:not(.skills-table)")
    .forEach(function (table) {
      var parent = table.parentElement;
      if (parent && parent.classList.contains("table-scroll")) return;
      var wrap = document.createElement("div");
      wrap.className = "table-scroll";
      table.parentNode.insertBefore(wrap, table);
      wrap.appendChild(table);
    });

  if (!prefersReduced && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll(
      ".site-hero, #main .post, #sidebar .widget, #secondary .widget, .resume-page .resume-block"
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
