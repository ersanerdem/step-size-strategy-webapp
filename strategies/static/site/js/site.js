/* Shared page behaviour: light / dark theme switch. */
(function () {
  "use strict";

  var root = document.documentElement;
  var toggle = document.getElementById("theme-toggle");

  function setTheme(theme) {
    root.setAttribute("data-bs-theme", theme);
    try { window.localStorage.setItem("theme", theme); } catch (e) { /* storage may be blocked */ }
    document.dispatchEvent(new CustomEvent("themechange", { detail: { theme: theme } }));
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setTheme(root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark");
    });
  }

  /* Suggest the Turkish page to visitors whose browser prefers Turkish (no automatic redirect:
     search engines and people who chose English keep the English page). */
  var hint = document.getElementById("lang-hint");
  if (hint) {
    var wanted = hint.getAttribute("data-suggest");
    var languages = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    var prefersWanted = String(languages[0] || "").toLowerCase().indexOf(wanted) === 0;
    var dismissed = false;
    try { dismissed = window.localStorage.getItem("langHintDismissed") === "1"; } catch (e) {}
    if (prefersWanted && !dismissed) { hint.classList.remove("d-none"); }
    var close = document.getElementById("lang-hint-close");
    if (close) {
      close.addEventListener("click", function () {
        hint.classList.add("d-none");
        try { window.localStorage.setItem("langHintDismissed", "1"); } catch (e) {}
      });
    }
  }
})();
