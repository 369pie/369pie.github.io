(function () {
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav-menu");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var path = window.location.pathname.replace(/\/$/, "") || "/";
  if (!nav) return;
  var links = nav.querySelectorAll("a[href]");
  links.forEach(function (link) {
    var href = link.getAttribute("href").replace(/\/$/, "") || "/";
    if (href === path || (href !== "/" && path.indexOf(href) === 0)) {
      link.classList.add("current");
    }
  });
})();
