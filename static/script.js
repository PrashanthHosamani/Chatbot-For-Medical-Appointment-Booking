// DOM Elements
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
const navbar = document.querySelector('.navbar');

// Navigation Toggle
hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    hamburger.classList.toggle('active');
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('active');
        hamburger.classList.remove('active');
    }
});

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Sticky Navigation with Progress Bar
let lastScroll = 0;
const progressBar = document.createElement('div');
progressBar.className = 'scroll-progress';
document.body.appendChild(progressBar);

window.addEventListener('scroll', () => {
    // Sticky Nav Logic
    const currentScroll = window.pageYOffset;
    if (currentScroll > 100) {
        navbar.style.background = 'rgba(255,255,255,0.95)';
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    } else {
        navbar.style.background = 'white';
        navbar.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
    }

    // Hide/Show Nav on Scroll
    if (currentScroll > lastScroll && currentScroll > 500) {
        navbar.style.top = '-80px';
    } else {
        navbar.style.top = '0';
    }
    lastScroll = currentScroll;

    // Update Progress Bar
    const scrolled = (currentScroll / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    progressBar.style.width = `${scrolled}%`;
});

// Lazy Loading Images
document.addEventListener('DOMContentLoaded', () => {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
});

// Animate on Scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.classList.add('animated');
        }
    });
};

window.addEventListener('scroll', animateOnScroll);

// Form Validation
function validateForm(formData) {
    const errors = {};
    
    // Name validation
    if (!formData.name || formData.name.trim().length < 2) {
        errors.name = 'Name must be at least 2 characters long';
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
        errors.email = 'Please enter a valid email address';
    }
    
    // Phone validation
    const phoneRegex = /^\d{10}$/;
    if (!formData.phone || !phoneRegex.test(formData.phone)) {
        errors.phone = 'Please enter a valid 10-digit phone number';
    }
    
    return errors;
}

// Date Validation
function isValidDate(dateString) {
    const regex = /^\d{2}\/\d{2}\/\d{4}$/;
    if (!regex.test(dateString)) return false;
    
    const [day, month, year] = dateString.split('/').map(Number);
    const date = new Date(year, month - 1, day);
    const today = new Date();
    
    return date >= today && 
           date.getDate() === day &&
           date.getMonth() === month - 1 &&
           date.getFullYear() === year;
}

// Chatbot Navigation
function openChatbot() {
    window.location.href = '/chatbot';
}

// Add CSS classes for animations
document.querySelectorAll('.service-card, .doctor-card, .feature-card').forEach(card => {
    card.classList.add('animate-on-scroll');
});

// Tooltip Implementation
const tooltips = document.querySelectorAll('[data-tooltip]');
tooltips.forEach(element => {
    element.addEventListener('mouseenter', e => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = element.dataset.tooltip;
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
        tooltip.style.left = `${rect.left + (rect.width/2) - (tooltip.offsetWidth/2)}px`;
        
        element.addEventListener('mouseleave', () => tooltip.remove());
    });
});

// Add to your existing script.js
function validateAppointmentForm() {
    const requiredFields = ['name', 'email', 'phone', 'department', 'doctor', 'date', 'time'];
    let isValid = true;
    
    requiredFields.forEach(field => {
        const input = document.getElementById(field);
        if (!input || !input.value.trim()) {
            isValid = false;
            if (input) {
                input.classList.add('error');
            }
        }
    });
    
    return isValid;
}

// Error Handling
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// Success Message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Add CSS for new elements
const style = document.createElement('style');
style.textContent = `
    .scroll-progress {
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: var(--primary-color);
        z-index: 1001;
        transition: width 0.3s;
    }
    
    .tooltip {
        position: fixed;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 14px;
        pointer-events: none;
        z-index: 1000;
    }
    
    .error-message, .success-message {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 20px;
        border-radius: 5px;
        animation: slideIn 0.3s ease-out;
    }
    
    .error-message {
        background: #dc3545;
        color: white;
    }
    
    .success-message {
        background: #28a745;
        color: white;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
`;

document.head.appendChild(style);