function formatLocalDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function setDefaultDates() {
  document.querySelectorAll('input[type="date"][data-default-days]').forEach((input) => {
    if (input.value) return;
    const days = Number(input.dataset.defaultDays || 0);
    const date = new Date();
    date.setDate(date.getDate() + days);
    input.value = formatLocalDate(date);
  });
}

function bindMobileNav() {
  const nav = document.getElementById("mobileNav");
  const toggle = document.querySelector("[data-mobile-toggle]");
  if (!nav || !toggle) return;

  toggle.addEventListener("click", () => {
    nav.classList.toggle("open");
    document.body.style.overflow = nav.classList.contains("open") ? "hidden" : "";
  });

  document.querySelectorAll("[data-mobile-close]").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      document.body.style.overflow = "";
    });
  });
}

function bindNavbarScroll() {
  const navbar = document.getElementById("navbar");
  if (!navbar) return;

  const update = () => {
    navbar.style.background = window.scrollY > 50 ? "rgba(8,8,16,0.98)" : "rgba(8,8,16,0.9)";
  };

  update();
  window.addEventListener("scroll", update, { passive: true });
}

function hideFlashesLater() {
  setTimeout(() => {
    document.querySelectorAll(".flash").forEach((flash) => {
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-8px)";
      flash.style.transition = "opacity 0.25s ease, transform 0.25s ease";
    });
  }, 4500);
}

setDefaultDates();
bindMobileNav();
bindNavbarScroll();
hideFlashesLater();
