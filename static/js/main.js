/* ========================================================================
   GOBIERNO DIGITAL 2026 - MAGIA UI INTERACTIVA
   ======================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    
    // 1. ANIMACIÓN DE ENTRADA EN CASCADA PARA PANELES Y TARJETAS
    const elementosAnimables = document.querySelectorAll('.card, .panel, .ticket-card, .formulario-container');
    
    elementosAnimables.forEach((el, index) => {
        // Preparamos los elementos para la animación
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
        
        // Retrasamos la animación de cada uno para que entren en "cascada"
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * index); // 100ms de retraso entre cada tarjeta
    });

    // 2. EFECTO RIPPLE (ONDA DE AGUA) EN TODOS LOS BOTONES
    const botones = document.querySelectorAll('.btn-accion, .btn-guardar, .btn-ingresar, .btn-flotante, .dt-button');
    
    botones.forEach(boton => {
        // Aseguramos que el botón pueda contener el efecto
        if(window.getComputedStyle(boton).position === 'static') {
            boton.style.position = 'relative';
        }
        boton.style.overflow = 'hidden';

        boton.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            
            // Calculamos la posición del clic
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Creamos el elemento de la onda
            const ripple = document.createElement('span');
            ripple.style.position = 'absolute';
            ripple.style.background = 'rgba(255, 255, 255, 0.4)';
            ripple.style.borderRadius = '50%';
            ripple.style.pointerEvents = 'none';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.width = '0px';
            ripple.style.height = '0px';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.style.transition = 'width 0.4s ease-out, height 0.4s ease-out, opacity 0.6s ease-out';
            
            this.appendChild(ripple);
            
            // Forzamos el reflow para que corra la animación
            setTimeout(() => {
                const size = Math.max(rect.width, rect.height) * 2.5;
                ripple.style.width = `${size}px`;
                ripple.style.height = `${size}px`;
                ripple.style.opacity = '0';
            }, 10);
            
            // Limpiamos el span después de la animación
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // 3. MEJORA EN LOS INPUTS (Efecto de etiqueta activa)
    const inputs = document.querySelectorAll('input[type="text"], input[type="date"], select, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.style.transform = 'scale(1.02)';
            input.parentElement.style.transition = 'transform 0.2s';
        });
        input.addEventListener('blur', () => {
            input.parentElement.style.transform = 'scale(1)';
        });
    });
});