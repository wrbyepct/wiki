window.document.addEventListener("DOMContentLoaded", () => {

     // Add start-transition after page loaded 
     const elements = document.querySelectorAll('[aria-label="transition-btn"]');
     elements.forEach((el) => {
        el.classList.add('start-transition');
        console.log(`add ${el} for start transition`)
     })
    

    // Page entry deletion confirmation button
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

    // Add ease out transition to alert message 
    const message = document.getElementById('alertMessage')
    console.log(message)
    if (message) {
        setTimeout(() => {
            message.classList.add('out');
            message.style.maxHeight = '0'

            // Add display none to not occupy the space
            setTimeout(() => {
                message.style.display = 'none';
                
            }, 400)
            
        }, 2000)
    }

})
