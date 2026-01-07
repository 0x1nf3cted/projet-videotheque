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
});
