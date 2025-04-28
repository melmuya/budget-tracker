// static/app.js

document.addEventListener('DOMContentLoaded', function() {
    // Show loading spinner when forms are submitted
    const forms = document.querySelectorAll('form');
    const body = document.body;
    
    // Create the loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = '<div class="spinner"></div>';
    body.appendChild(loadingOverlay);
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            loadingOverlay.classList.add('show');
        });
    });
    
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-links a');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Format currency in expense table
    const amountCells = document.querySelectorAll('.expense-table td:nth-child(2)');
    amountCells.forEach(cell => {
        const amount = parseFloat(cell.textContent);
        if (!isNaN(amount)) {
            cell.textContent = 'Ksh ' + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
    });
    
    // Enhance chart animation if it exists
    const chartElement = document.getElementById('expenseChart');
    if (chartElement) {
        // Add subtle animation when user hovers over chart
        chartElement.addEventListener('mousemove', function(e) {
            const rect = chartElement.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Calculate distance from center
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Calculate tilt based on mouse position
            const tiltX = (y - centerY) / 30;
            const tiltY = (centerX - x) / 30;
            
            // Apply subtle 3D rotation
            chartElement.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
        });
        
        // Reset transform when mouse leaves
        chartElement.addEventListener('mouseleave', function() {
            chartElement.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
        });
    }
});

// Add responsive category badges
function addCategoryBadgeColors() {
    const categories = document.querySelectorAll('[data-category]');
    categories.forEach(element => {
        const category = element.dataset.category.toLowerCase();
        const badgeColors = {
            'food': ['#28c76f', 'rgba(40, 199, 111, 0.1)'],
            'transport': ['#5661f1', 'rgba(86, 97, 241, 0.1)'],
            'entertainment': ['#7367f0', 'rgba(115, 103, 240, 0.1)'],
            'health': ['#ea5455', 'rgba(234, 84, 85, 0.1)'],
            'utilities': ['#ff9f43', 'rgba(255, 159, 67, 0.1)'],
            'shopping': ['#00cfe8', 'rgba(0, 207, 232, 0.1)'],
            'other': ['#82868b', 'rgba(130, 134, 139, 0.1)']
        };
        
        // If category exists in our map, apply the color
        if (badgeColors[category]) {
            element.style.borderLeftColor = badgeColors[category][0];
        }
    });
}

// Call on page load
addCategoryBadgeColors();