function toggleTab(tabName) {
  const borrowedTab = document.getElementById('borrowed-tab');
  const returnedTab = document.getElementById('returned-tab');

  // Toggle class
  borrowedTab.classList.toggle('active', tabName === 'borrowed');
  returnedTab.classList.toggle('active', tabName === 'returned');

  // Show/hide sections
  document.getElementById('borrowed-section').style.display = (tabName === 'borrowed') ? 'block' : 'none';
  document.getElementById('returned-section').style.display = (tabName === 'returned') ? 'block' : 'none';
}
