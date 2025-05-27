Chart.register(ChartDataLabels); // register the plugin
Chart.defaults.font.family = 'Montserrat'; // set once

// For visualizing the dashboard charts
function loadDashboardCharts(data) {
    // Return Ratio Pie Chart
    const returnCtx = document.getElementById('returnRatioChart');
    if (returnCtx && data.returnValues.length > 0) {
        new Chart(returnCtx.getContext('2d'), {
            type: 'pie',
            data: {
            labels: data.returnLabels,
            datasets: [{
                data: data.returnValues,
                backgroundColor: ["#535878","#9db0ce","#b8d8e3"],
                hoverOffset: 15  
            }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                            display: true,
                            text: 'Loan Status Distribution',  
                            font: {
                                size: 18,
                                weight: 'bold',
                                family: 'Montserrat',
                            },
                            color: '#333',
                            padding: {
                                bottom: 20
                            }
                    },
                    
                    legend: {
                        position: 'right',  
                        labels: {
                            color: '#333',  
                            font: {
                                family: 'Montserrat',
                                size: 14,
                                weight: 'bold'
                            },
                            usePointStyle: true  
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const value = context.parsed;
                                return ` ${value} books)`;  
                            }
                        }
                    },
                    datalabels: {
                        color: '#fff',
                        formatter: (value, context) => {
                            const data = context.chart.data.datasets[0].data;
                            const total = data.reduce((a, b) => a + b, 0);
                            const percent = (value / total * 100).toFixed(1);
                            return `${percent}%`;
                        },
                        font: {
                            family: 'Montserrat',
                            weight: 'bold'
                        }
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

    // Genre Distribution Pie Chart
    const genreCtx = document.getElementById('genreChart');
    if (genreCtx) {
            new Chart(genreCtx.getContext('2d'), {
            type: 'pie',
            data: {
                labels: data.genreLabels,
                datasets: [{
                    data: data.genreValues,
                    backgroundColor: ["#535878","#9db0ce","#b8d8e3","#fee1dd","#e9c2c5","#cea0aa"],
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                            display: true,
                            text: 'Your Book Genre Distribution',  
                            font: {
                                size: 18,
                                weight: 'bold',
                                family: 'Montserrat',
                            },
                            color: '#333',
                            padding: {
                                bottom: 20
                            }
                    },
                    
                    legend: {
                        position: 'right',  
                        labels: {
                            color: '#333',  
                            font: {
                                family: 'Montserrat',
                                size: 14,
                                weight: 'bold'
                            },
                            usePointStyle: true  
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const value = context.parsed;
                                return ` ${value} books)`;  
                            }
                        }
                    },
                    datalabels: {
                        color: '#fff',
                        formatter: (value, context) => {
                            const data = context.chart.data.datasets[0].data;
                            const total = data.reduce((a, b) => a + b, 0);
                            const percent = (value / total * 100).toFixed(1);
                            return `${percent}%`;
                        },
                        font: {
                            family: 'Montserrat',
                            weight: 'bold'
                        }
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

    // Borrow Activity Bar Chart

    data.borrowLabels = data.borrowLabels.map(dateStr => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });

    const borrowCtx = document.getElementById('borrowChart');
    if (borrowCtx && data.borrowValues.length > 0) {
    new Chart(borrowCtx.getContext('2d'), {
        type: 'line',
        data: {
            labels: data.borrowLabels,
            datasets: [{
                label: 'Books Borrowed',
                data: data.borrowValues,
                borderColor: '#9db0ce',
                borderWidth: 2,
                tension: 0,     // Smooth line
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
            title:{
                display: true,
                text: 'Books Borrowed Over Time',
                font: {
                    size: 18,
                    weight: 'bold',
                    family: 'Montserrat',
                },
                color: '#333',
                padding: {
                    bottom: 20
                }
            },
            legend: {
                display: false
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                bodyFont: {
                    family: 'Montserrat',
                    size: 14,
                },
                titleFont: {
                    family: 'Montserrat',
                    size: 16,
                    weight: 'bold'

                },
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
        },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Books',
                        font: {
                            family: 'Montserrat',
                            size: 14,
                        }
                    },
                    grid: {
                        color: '#eee'
                    }
                },
                x: {
                    title: {
                        display: false,
                        font: {
                            family: 'Montserrat',
                            size: 14
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        }
    });
}
}

// For collapsing the sidebar
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleSidebar');

  if (sidebar && toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }
});