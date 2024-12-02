
// Burgermenu open/close function
// Ensure the DOM is fully loaded before running the script
  document.addEventListener("DOMContentLoaded", () => {
    const burgerMenuButton = document.querySelector('.burger-menu-btn'); // Burger button
    const menu = document.querySelector('.menu'); // Menu to toggle

    // Check if elements exist to avoid errors
    if (burgerMenuButton && menu) {
        burgerMenuButton.addEventListener('click', () => {
            menu.classList.toggle('open'); // Toggle the "open" class on the menu
        });
    }
});



// redirects button links in header
document.getElementById("signupButton").addEventListener("click", function() {
    navigateTo("{{ url_for('edit_profile') }}");
});

document.getElementById("loginButton").addEventListener("click", function() {
    navigateTo("{{ url_for('edit_profile') }}");
    console.log("hello")
});

function navigateTo(path) {
    window.location.href = path; // Navigates to the provided path
}