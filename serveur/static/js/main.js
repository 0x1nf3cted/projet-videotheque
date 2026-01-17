function afficherMessage(type, message) {
    const main = document.querySelector('main');
    if (!main) return;
    
    const div = document.createElement('div');
    div.className = `alert alert-${type}`;
    div.textContent = message;
    
    const flashMessages = main.querySelector('.flash-messages') || document.createElement('div');
    flashMessages.className = 'flash-messages';
    flashMessages.appendChild(div);
    
    if (!main.querySelector('.flash-messages')) {
        main.insertBefore(flashMessages, main.firstChild);
    }
    
    setTimeout(() => {
        div.remove();
    }, 5000);
}

document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    const dropdown = document.querySelector('.dropdown');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    if (dropdown && dropdownMenu) {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        let isOpen = false;
        
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            isOpen = !isOpen;
            if (isOpen) {
                dropdownMenu.classList.add('show');
            } else {
                dropdownMenu.classList.remove('show');
            }
        });

        dropdownMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target) && isOpen) {
                dropdownMenu.classList.remove('show');
                isOpen = false;
            }
        });
    }
});
