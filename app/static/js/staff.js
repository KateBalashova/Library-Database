Chart.register(ChartDataLabels);
Chart.defaults.font.family = 'Montserrat';

function loadStaffDashboard(data) {
  // Format loan chart date labels
  const loanLabels = data.loanLabels.map(dateStr => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  });

  // Loan Activity Line Chart
  const loanCtx = document.getElementById('loanChart');
  if (loanCtx && data.loanValues.length > 0) {
    new Chart(loanCtx.getContext('2d'), {
      type: 'line',
      data: {
        labels: loanLabels,
        datasets: [{
          label: 'Loans per Day',
          data: data.loanValues,
          borderColor: '#9db0ce',
          borderWidth: 2,
          tension: 0.3,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: 'white',
          pointBorderColor: '#9db0ce',
          pointBorderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Loan Activity This Week',
            font: { size: 18, weight: 'bold' },
            color: '#333',
            padding: { bottom: 20 }
          },
          legend: { display: false },
          tooltip: {
            bodyFont: { family: 'Montserrat', size: 14 },
            titleFont: { family: 'Montserrat', size: 16, weight: 'bold' }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Loans',
              font: { family: 'Montserrat', size: 14 }
            },
            grid: { color: '#eee' }
          },
          x: {
            title: { display: false },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Genre Distribution Chart
  const genreCtx = document.getElementById('genreDistChart');
  if (genreCtx && data.genreValues?.length > 0) {
    new Chart(genreCtx.getContext('2d'), {
      type: 'pie',
      data: {
        labels: data.genreLabels,
        datasets: [{
          data: data.genreValues,
          backgroundColor: ["#535878", "#9db0ce", "#b8d8e3", "#fee1dd", "#e9c2c5", "#cea0aa"],
          hoverOffset: 15
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Genre Distribution',
            font: { size: 18, weight: 'bold' },
            color: '#333',
            padding: { bottom: 20 }
          },
          legend: {
            position: 'right',
            labels: {
              color: '#333',
              font: { size: 14, weight: 'bold' },
              usePointStyle: true
            }
          },
          tooltip: {
            callbacks: {
              label: context => ` ${context.parsed} books`
            }
          },
          datalabels: {
            color: '#fff',
            formatter: (value, context) => {
              const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              return `${((value / total) * 100).toFixed(1)}%`;
            },
            font: { weight: 'bold' }
          }
        },
        animations: {
          animateRotate: true,
          duration: 1200,
          easing: 'easeOutBounce'
        }
      },
      plugins: [ChartDataLabels]
    });
  }

  // Book Status Pie Chart
  const statusCtx = document.getElementById('statusPieChart');
  if (statusCtx && data.statusValues?.length > 0) {
    new Chart(statusCtx.getContext('2d'), {
      type: 'pie',
      data: {
        labels: data.statusLabels,
        datasets: [{
          data: data.statusValues,
          backgroundColor: ["#535878", "#9db0ce", "#b8d8e3", "#fee1dd", "#e9c2c5", "#cea0aa"],
          hoverOffset: 15
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Book Status Breakdown',
            font: { size: 18, weight: 'bold' },
            color: '#333',
            padding: { bottom: 20 }
          },
          legend: {
            position: 'right',
            labels: {
              color: '#333',
              font: { size: 14, weight: 'bold' },
              usePointStyle: true
            }
          },
          tooltip: {
            callbacks: {
              label: context => ` ${context.parsed} books`
            }
          },
          datalabels: {
            color: '#fff',
            formatter: (value, context) => {
              const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              return `${((value / total) * 100).toFixed(1)}%`;
            },
            font: { weight: 'bold' }
          }
        },
        animations: {
          animateRotate: true,
          duration: 1200,
          easing: 'easeOutBounce'
        }
      },
      plugins: [ChartDataLabels]
    });
  }
}

function openAddModal() {
  document.getElementById("bookForm").reset();
  document.getElementById("bookModalLabel").innerText = "Add New Book";
  document.getElementById("book_id").value = "";
  document.getElementById("copies").disabled = false;
}


function openEditModal(book) {
  document.getElementById("bookModalLabel").innerText = "Edit Book";
  document.getElementById("book_id").value = book.book_id;
  document.getElementById("title").value = book.title || '';
  document.getElementById("isbn").value = book.isbn || '';
  document.getElementById("authors").value = book.authors || '';
  document.getElementById("genres").value = book.genres || '';
  document.getElementById("publication_year").value = book.publication_year || '';
  document.getElementById("language").value = book.language || '';
  document.getElementById("num_pages").value = book.num_pages || '';
  document.getElementById("copies").value = book.total_copies || 0;
  document.getElementById("copies").min = book.total_copies || 0;
  document.getElementById("copy-warning").style.display = "none";

  const modal = new bootstrap.Modal(document.getElementById("bookModal"));
  modal.show();
}


function openStatusModal(bookId) {
  // Save book_id to hidden input
  document.getElementById("modal_book_id").value = bookId;

  // Fetch all book items for that book via AJAX (optional), or embed beforehand
  fetch(`/staff/book/${bookId}/items`)
    .then(res => res.json())
    .then(data => {
      const dropdown = document.getElementById("book_item_id");
      dropdown.innerHTML = "";
      data.items.forEach(item => {
        const option = document.createElement("option");
        option.value = item.book_item_id;
        option.text = `ID: ${item.book_item_id} (${item.status})`;
        dropdown.appendChild(option);
      });

      // Show modal
      const modal = new bootstrap.Modal(document.getElementById("statusModal"));
      modal.show();
    });
}

// Confirmation before submitting edit/add
document.addEventListener("DOMContentLoaded", () => {
  const bookForm = document.getElementById("bookForm");
  if (bookForm) {
    bookForm.addEventListener("submit", function (event) {
      const isEdit = document.getElementById("book_id").value !== "";
      const message = isEdit
        ? "Are you sure you want to update this book's information?"
        : "Are you sure you want to add this book and its copies?";
      if (!confirm(message)) {
        event.preventDefault();
      }
    });
  }

  // Auto-dismiss flash messages
  const flashContainer = document.getElementById("flash-container");
  if (flashContainer) {
    setTimeout(() => {
      flashContainer.innerHTML = "";
    }, 3000); // fade after 3s
  }
});

// Confirmation for Approve/Decline actions
function confirmApprove() {
  console.log("Approve confirm triggered");
  return confirm("Are you sure you want to approve this reservation?");
}

function confirmDecline() {
  console.log("Decline confirm triggered");
  return confirm("Are you sure you want to decline this reservation?");
}

function confirmReturn() {
  return confirm("Are you sure you want to return this book?");
}

// Auto-fade flash messages after 3 seconds
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      el.classList.remove('show');
      el.classList.add('fade');
      setTimeout(() => el.remove(), 500);
    });
  }, 3000);
});

document.addEventListener("DOMContentLoaded", () => {
  // Read the URL parameter ?tab=...
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get("tab");

  if (tab === "returns") {
    const returnsTab = document.querySelector('#returns-tab');
    const returnsPane = document.querySelector('#returns');

    const pendingTab = document.querySelector('#pending-tab');
    const pendingPane = document.querySelector('#pending');

    if (returnsTab && returnsPane && pendingTab && pendingPane) {
      // Bootstrap: activate returns tab
      pendingTab.classList.remove('active');
      pendingPane.classList.remove('show', 'active');

      returnsTab.classList.add('active');
      returnsPane.classList.add('show', 'active');
    }
  }
});
