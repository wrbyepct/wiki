window.document.addEventListener("DOMContentLoaded", () => {
    // Page entry deletion confirmation button
    document.getElementById("deleteEntry")
    .addEventListener("click", function(event) {
        if (!confirm("Are you sure to delete this entry?")) {
            event.preventDefault();
        }
    })
})
