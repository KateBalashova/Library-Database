function toggleTab(tabName) {
  const tabs = ['borrowed', 'returned', 'reserved'];

  tabs.forEach(name => {
    // Toggle tab button active class
    const tab = document.getElementById(name + '-tab');
    if (tab) {
      tab.classList.toggle('active', name === tabName);
    }

    // Toggle section visibility
    const section = document.getElementById(name + '-section');
    if (section) {
      section.style.display = (name === tabName) ? 'block' : 'none';
    }
  });
}

function confirmCancel(form) {
  const title = form.closest('tr').querySelector('td:nth-child(2)').innerText;
  return confirm(`Are you sure you want to cancel the reservation for "${title}"?`);
}

window.addEventListener("DOMContentLoaded", () => {
  const tab = new URLSearchParams(window.location.search).get("tab") || "borrowed";
  toggleTab(tab);
});
