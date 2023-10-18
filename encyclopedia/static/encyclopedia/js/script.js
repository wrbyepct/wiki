// Initialize local storage theme 


const applyTheme = () => {

    let theme = localStorage.getItem('theme');

    const themeBody = document.getElementById('theme');

    console.log(`Setting theme: ${theme}`);

   
    if (!theme) {
        theme = 'day';
    }
    
    if (themeBody) {

        try {
            themeBody.classList.add(theme)
        } catch (error) {
            console.error(error)
        }
        
    } else {
        console.error(`No such class ${themeBody} found`);
    }

}


// Toggle theme logic
const toggleTheme = () => {

    const toggle = document.querySelector('.toggle-wrapper');
    const themeBody = document.getElementById('theme');

    if (toggle && themeBody) {
        toggle.addEventListener('click', () => {

            themeBody.classList.toggle('night');
            themeBody.classList.toggle('day');

            const theme = themeBody.classList.value;
     
            localStorage.setItem('theme', theme);
        })

    } else {
        console.error("Now toggle button found");
    }

}


// Add start-transition after page loaded 
const applyTransitionEffect = () => {
    
    const elements = document.querySelectorAll('[aria-label="transition-btn"]');

    if (elements) {
        elements.forEach((el) => {
            el.classList.add('start-transition');
            console.log(`add ${el} for start transition`)
         })
    } else {

        console.error("No transition button found.")
    }

}


// Page entry deletion confirmation button
const confirmDeleteEntry = () => {

    const deleteBtn = document.getElementById("deleteEntry");

    if (deleteBtn) {
        deleteBtn.addEventListener("click", function(event) {
            if (!confirm("Are you sure to delete this entry?")) {
                event.preventDefault();
            }
        });
    } else {
        console.error("Element with ID 'deleteEntry' was not found.");
    }

}


const removeAlertMessage = () => {

   
    const message = document.getElementById('alertMessage')
  
    if (message) {
        console.log("removal of alert message called, setting timeout...")
        // Add display none to not occupy the space
        setTimeout(() => {
            message.classList.add('out');
        }, 2000)
        
        setTimeout(() => {
            message.remove()
        }, 2700)
        
    } else {
        console.error('No "alertMessage" class found')
    }

}


applyTheme();
document.addEventListener("DOMContentLoaded", () => {

    
    applyTransitionEffect();
    
    toggleTheme();
    
    confirmDeleteEntry();

    removeAlertMessage();

})
