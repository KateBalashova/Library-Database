function loadAdminDashboardCharts({ branchLabels, branchData, patronGrowthLabels, patronGrowthData, loanLabels, loanValues }) {
  // Branch Distribution Chart (Bar)
  new Chart(document.getElementById('branchChart'), {
    type: 'bar',
    data: {
      labels: branchLabels,
      datasets: [{
        label: 'Books per Branch',
        data: branchData,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Book Distribution by Branch',
          font: { size: 16 }
        },
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Book Count' }
        }
      }
    }
  });

  // Patron Growth Chart (Line)
  new Chart(document.getElementById('patronGrowthChart'), {
    type: 'line',
    data: {
      labels: patronGrowthLabels,
      datasets: [{
        label: 'New Patrons',
        data: patronGrowthData,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Patron Registration Over Time',
          font: { size: 16 }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Number of Patrons' }
        }
      }
    }
  });

  // Monthly Loans Chart (Line)
  new Chart(document.getElementById('monthlyLoansChart'), {
    type: 'line',
    data: {
      labels: loanLabels,
      datasets: [{
        label: 'Monthly Loans',
        data: loanValues,
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Loans per Month',
          font: { size: 16 }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Loans' }
        }
      }
    }
  });
}

function editPatron(patron) {
  // You can integrate this with a Bootstrap modal if needed
  const formHtml = `
    <p>Edit feature not yet implemented.<br>
    Patron: ${patron.first_name} ${patron.last_name}</p>
  `;
  alert(formHtml);
}

function openEditStaffModal(staff) {
  document.getElementById('editStaffId').value = staff.staff_id;
  document.getElementById('editFirstName').value = staff.first_name;
  document.getElementById('editLastName').value = staff.last_name;
  document.getElementById('editPhone').value = staff.phone;
  document.getElementById('editRole').value = staff.role;
  document.getElementById('editBranch').value = staff.branch_id;

  // Open modal
  const modal = new bootstrap.Modal(document.getElementById('editStaffModal'));
  modal.show();
}