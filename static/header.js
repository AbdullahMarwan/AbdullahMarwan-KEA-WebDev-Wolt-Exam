
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


document.addEventListener('DOMContentLoaded', function() {
    // Select all 'Add to cart' buttons
    const addToCartButtons = document.querySelectorAll('.item-card .buy');

    // Initialize total price
    let totalPriceValue = 0;

    // Add event listener to each button
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the parent item card
            const itemCard = this.closest('.item-card');
            
            // Get item details (e.g., item_pk, title, price, image)
            const itemPk = itemCard.getAttribute('data-item-pk');
            const itemTitle = itemCard.querySelector('.card-title').textContent;
            const itemPrice = parseFloat(itemCard.querySelector('.card-price').textContent.replace(' kr.', '').trim());
            const itemImage = itemCard.querySelector('.card-img').src;
            
            // Create a new item element for the cart
            const cartItem = document.createElement('div');
            cartItem.classList.add('cart-item');
            cartItem.setAttribute('data-item-pk', itemPk);
            
            cartItem.innerHTML = `
                <img src="${itemImage}" alt="${itemTitle}" class="cart-item-img"/>
                <div class="cart-item-content">
                    <h3 class="cart-item-title">${itemTitle}</h3>
                    <p class="cart-item-price">${itemPrice} kr.</p>
                </div>
            `;
            
            // Append the new item to the cart list
            const cartList = document.querySelector('.cart-list .item-list-cart');
            cartList.appendChild(cartItem);
            
            // Update the total price
            totalPriceValue += itemPrice;
            document.getElementById('total-price').textContent = "Total Price: " + totalPriceValue.toFixed(2);
        });
    });
});





document.addEventListener('DOMContentLoaded', function() {
    const cartList = document.querySelector('.cart-list');
    const toggleButton = document.querySelector('#toggle-cart');  // The button that triggers the animation


    // Ensure the elements exist before adding event listener
    if (cartList && toggleButton) {
        toggleButton.addEventListener('click', () => {

            // If the cart is hidden, slide it in and make it visible
            if (cartList.classList.contains('slide-in')) {
                cartList.classList.remove('slide-in');  // Remove 'hidden'
                cartList.classList.add('slide-out');   // Add 'slide-in'
            } else if (cartList.classList.contains('slide-out')) {
                cartList.classList.remove('slide-out');  // Remove 'slide-in'
                cartList.classList.add('slide-in');    // Add 'slide-out'
            } else
            console.log("After toggling: ", cartList.classList);  // Log after class removal or addition
        });
    } else {
        console.log("Element(s) not found.");
    }
});






    document.addEventListener('DOMContentLoaded', function() {
        const itemList = document.querySelector('.item-list-cart'); // Parent container
    
        itemList.addEventListener('click', function(event) {
            // Check if the clicked element is the button
            if (event.target && event.target.classList.contains('buy')) {
                event.preventDefault(); // Prevent default behavior
                console.log('Add to cart button clicked for item');
                // Add your add to cart logic here
            }
        });
    });