document.documentElement.classList.add("mpi-js");

const menu = document.querySelector(".mpi-menu-toggle");
const nav = document.querySelector("#mpi-nav");

function setMenu(open) {
  menu.setAttribute("aria-expanded", String(open));
  nav.dataset.open = String(open);
}

if (menu && nav) {
  menu.addEventListener("click", () => setMenu(menu.getAttribute("aria-expanded") !== "true"));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.getAttribute("aria-expanded") === "true") {
      setMenu(false);
      menu.focus();
    }
  });
}

function todayISO() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

const filters = document.querySelector(".mpi-filters");
if (filters) {
  const events = Array.from(document.querySelectorAll(".mpi-event"));
  const count = document.querySelector("#result-count");
  const heading = document.querySelector("#events-heading");
  const empty = document.querySelector("#no-results");

  function filterEvents() {
    const { region, age, kind, past } = filters.elements;
    const selectedAge = Number(age.value);
    const today = todayISO();
    let visible = 0;
    events.forEach((event) => {
      const regions = event.dataset.regions.split(" ");
      const matchesRegion = !region.value || regions.includes("worldwide") || regions.includes(region.value);
      // A missing age is unconfirmed. Keep the listing and let the organiser clarify.
      const matchesAge = !selectedAge || !event.dataset.min ||
        (selectedAge >= Number(event.dataset.min) && selectedAge <= Number(event.dataset.max));
      const matchesKind = !kind.value || event.dataset.kind === kind.value;
      const matchesDate = past.checked || event.dataset.date >= today;
      event.hidden = !(matchesRegion && matchesAge && matchesKind && matchesDate);
      if (!event.hidden) visible += 1;
    });
    heading.textContent = past.checked ? "All events" : "Upcoming events";
    count.textContent = visible === 1 ? "1 event" : `${visible} events`;
    empty.hidden = visible > 0;
  }

  function openLinkedEvent() {
    const event = events.find((item) => location.hash === `#${item.id}`);
    if (!event) return;
    if (event.hidden) {
      filters.reset();
      filters.elements.past.checked = event.dataset.date < todayISO();
      filterEvents();
    }
    event.open = true;
    event.scrollIntoView({ block: "start" });
  }

  filters.addEventListener("change", filterEvents);
  filters.addEventListener("reset", () => requestAnimationFrame(filterEvents));
  filters.addEventListener("submit", (event) => event.preventDefault());
  window.addEventListener("hashchange", openLinkedEvent);
  filterEvents();
  openLinkedEvent();
}

const upcoming = document.querySelector("[data-up-next]");
if (upcoming) {
  const calendarURL = upcoming.querySelector("a").href;
  const today = todayISO();
  fetch(calendarURL)
    .then((response) => {
      if (!response.ok) throw new Error("Calendar unavailable");
      return response.text();
    })
    .then((body) => {
      const calendar = new DOMParser().parseFromString(body, "text/html");
      const events = Array.from(calendar.querySelectorAll(".mpi-event"))
        .filter((event) => event.dataset.date >= today && (upcoming.dataset.upNext === "competition" ? event.dataset.kind === "competition" : event.dataset.kind !== "case writing"))
        .slice(0, 3);
      if (!events.length) return;
      const rows = events.map((event) => {
        const row = document.createElement("li");
        row.className = "mpi-event-row";
        const title = event.querySelector(".mpi-event-title").textContent;
        const metadata = event.querySelector(".mpi-event-meta").textContent;
        const text = document.createElement("div");
        const heading = document.createElement("h3");
        heading.textContent = title;
        const subline = document.createElement("p");
        subline.textContent = metadata;
        text.append(heading, subline);
        const link = document.createElement("a");
        link.className = "mpi-text-link";
        link.href = `${calendarURL}#${event.id}`;
        link.textContent = "Details →";
        link.setAttribute("aria-label", `Details for ${title}`);
        row.append(
          event.querySelector("time").cloneNode(true),
          text,
          event.querySelector(".mpi-event-type").cloneNode(true),
          link
        );
        return row;
      });
      upcoming.replaceChildren(...rows);
    })
    .catch(() => {
      // The calendar link remains available when fetching from a local file or offline.
    });
}

const resourceToggles = Array.from(document.querySelectorAll(".hb-header, .subject-header, .level-header"));
if (resourceToggles.length) {
  function syncResourceToggles() {
    for (const toggle of resourceToggles) {
      toggle.setAttribute("aria-expanded", String(toggle.nextElementSibling.classList.contains("open")));
    }
  }
  resourceToggles.forEach((toggle, index) => {
    const panel = toggle.nextElementSibling;
    panel.id ||= `resource-panel-${index + 1}`;
    toggle.setAttribute("role", "button");
    toggle.tabIndex = 0;
    toggle.setAttribute("aria-controls", panel.id);
    toggle.addEventListener("click", syncResourceToggles);
    toggle.addEventListener("keydown", (event) => {
      if (event.target === toggle && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault();
        toggle.click();
      }
    });
  });

  function openHandbookTarget() {
    const anchor = document.getElementById(location.hash.slice(1));
    if (!anchor) return;
    const handbook = document.querySelector(".hb-header");
    const wrapper = handbook?.parentElement;
    if (wrapper?.contains(anchor) && !wrapper.classList.contains("open")) handbook.click();
    if (wrapper?.contains(anchor)) anchor.scrollIntoView({ block: "start" });
  }

  syncResourceToggles();
  openHandbookTarget();
  window.addEventListener("hashchange", openHandbookTarget);
}
