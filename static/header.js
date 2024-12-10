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



document.addEventListener('DOMContentLoaded', function () {
    const numberOfProductsElement = document.querySelector('.number-of-products');
    const productNumberCtn = document.querySelector('.number-products-ctn');
    const cartList = document.querySelector('.cart-list .item-list-cart');
    const addToCartButtons = document.querySelectorAll('.buy');
    const totalPriceField = document.querySelector(".total-price");
    let numberOfProducts = 0;
    let totalPriceValue = 0;

    // Function to update the visibility of the product number container
    function updateProductNumberVisibility() {
        numberOfProductsElement.textContent = numberOfProducts;

        if (numberOfProducts === 0) {
            productNumberCtn.classList.add('hidden');
        } else {
            productNumberCtn.classList.remove('hidden');
        }
    }


    // Fetch cart data from the server
    async function fetchCartData() {
        try {
            const response = await fetch('/get_cart');
            const data = await response.json();

            console.log('Cart data from server:', data.cart);

            if (data.cart && data.cart.length > 0) {
                // Update the number of products based on the server array
                numberOfProducts = data.cart.length;
                numberOfProductsElement.textContent = numberOfProducts;

                // Clear the cart list and re-render items
                cartList.innerHTML = '';
                totalPriceValue = 0; // Reset total price before recalculating
                data.cart.forEach((item) => {
                    const cartItem = document.createElement('div');
                    cartItem.classList.add('cart-item');
                    cartItem.setAttribute('data-item-pk', item.pk);

                    cartItem.innerHTML = `
                        <img src="${item.image}" alt="${item.title}" class="cart-item-img"/>
                        <div class="cart-item-content">
                            <h4 class="cart-item-title">${item.title}</h4>
                            <p class="cart-item-price">${item.price} kr.</p>
                        </div>
                        <button class="cross-icon-btn">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M7 17L16.8995 7.10051" stroke="#fff" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M7 7.00001L16.8995 16.8995" stroke="#fff" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    `;

                    // Add event listener to the remove button
                    const removeButton = cartItem.querySelector('.cross-icon-btn');
                    
                    removeButton.addEventListener('click', function () {
                        const itemPk = cartItem.getAttribute('data-item-pk'); // Fetch the pk from the DOM
                        const itemPrice = parseFloat(cartItem.querySelector('.cart-item-price').textContent.replace(' kr.', '').trim());
                        removeItem(itemPk, itemPrice, cartItem);
                        console.log(itemPk);
                    });

                    // Accumulate total price
                    totalPriceValue += item.price;
                    cartList.appendChild(cartItem);
                });

                // Update total price in the DOM
                data.cart.js
                totalPriceField.textContent = `Total Price: ${totalPriceValue.toFixed(2)} kr.`;                
                const cartArray = data.cart;
                buyItems(totalPriceField.textContent, cartArray);
                // Output: [{ title: "Item 1", price: 100 }]

                // Ensure visibility reflects the updated count
                updateProductNumberVisibility();
            } else {
                // If the cart is empty, reset the count and hide the display
                numberOfProducts = 0;
                totalPriceValue = 0; // Reset total price
                numberOfProductsElement.textContent = numberOfProducts;
                totalPriceField.textContent = `Total Price: ${totalPriceValue.toFixed(2)} kr.`;
                updateProductNumberVisibility();
                console.warn('No items in the cart.');
            }
        } catch (error) {
            console.error('Error fetching cart data:', error);
        }
    }

 

    async function removeItem(itemPk, itemPrice, cartItemElement) {
        try {
            // Remove the item visually
            cartItemElement.remove();
    
            // Decrease the total price and update the display
            totalPriceValue -= itemPrice;
            totalPriceField.textContent = `Total Price: ${totalPriceValue.toFixed(2)} kr.`;
    
            // Decrease the product count and update visibility
            numberOfProducts--;
            updateProductNumberVisibility();
    
            // Update the backend
            const rawResponse = await fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    pk: itemPk
                    

                 }),
            });
    
            const content = await rawResponse.json();
            console.log('Server response after removal:', content);
        } catch (error) {
            console.error('Error removing item:', error);
        }
    }


    

    // Add event listeners to "Add to Cart" buttons
    addToCartButtons.forEach((button) => {
        button.addEventListener('click', async function () {
            const itemCard = this.closest('.item-card');
            const itemPk = itemCard.getAttribute('data-item-pk');
            const itemTitle = itemCard.querySelector('.card-title').textContent;
            const itemPrice = parseFloat(
                itemCard
                    .querySelector('.card-price')
                    .textContent.replace(' kr.', '')
                    .trim()
            );
            const itemImage = itemCard.querySelector('.card-img').src;
    
            const newCartItem = {
                pk: itemPk,
                title: itemTitle,
                price: itemPrice,
                image: itemImage,
            };
    
            console.log('Adding item:', newCartItem);
    
            button.disabled = true; // Disable button to prevent multiple clicks
    
            try {
                const rawResponse = await fetch('/add_to_cart', {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ cart: [newCartItem] }),
                });
                const content = await rawResponse.json();
    
                if (rawResponse.ok) {
                    console.log('Server response:', content);
    
                    const cartItem = document.createElement('div');
                    cartItem.classList.add('cart-item');
                    cartItem.setAttribute('data-item-pk', itemPk);
    
                    cartItem.innerHTML = `
                        <img src="${itemImage}" alt="${itemTitle}" class="cart-item-img"/>
                        <article class="cart-item-content">
                            <h4 class="cart-item-title">${itemTitle}</h4>
                            <p class="cart-item-price">${itemPrice} kr.</p>
                        </article>
                        <button class="cross-icon-btn">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M7 17L16.8995 7.10051" stroke="#fff" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M7 7.00001L16.8995 16.8995" stroke="#fff" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    `;
    
                    cartList.appendChild(cartItem);

                        // Add event listener to the remove button
                        const removeButton = cartItem.querySelector('.cross-icon-btn');
    
                        removeButton.addEventListener('click', function () {
                            const itemPk = cartItem.getAttribute('data-item-pk'); // Fetch the pk from the DOM
                            const itemPrice = parseFloat(cartItem.querySelector('.cart-item-price').textContent.replace(' kr.', '').trim());
                            removeItem(itemPk, itemPrice, cartItem);
                            console.log(itemPk);
                        });
    
                    totalPriceValue += itemPrice;
                    totalPriceField.textContent = `Total Price: ${totalPriceValue.toFixed(2)} kr.`;
                    numberOfProducts++;
                    updateProductNumberVisibility();
                } else {
                    console.error('Server failed to add item:', content.error);
                }
            } catch (error) {
                console.error('Error adding to cart:', error);
            } finally {
                button.disabled = false; // Re-enable button
            }
        });
    });
    

    // Initial call to fetch cart data
    fetchCartData();
});




// Toggle cart visibility
document.addEventListener('DOMContentLoaded', function () {
    const cartList = document.querySelector('.cart-list');
    const toggleButton = document.querySelector('#toggle-cart');

    if (cartList && toggleButton) {
        toggleButton.addEventListener('click', () => {
            cartList.classList.toggle('slide-in');
        });
    } else {
        cartList.classList.toggle('slide-out');
        console.log("Element(s) not found.");
    }
});





async function buyItems(totalPriceField, items) {
    const buyBtn = document.querySelector(".buy-btn");
    buyBtn.addEventListener("click", async () => {
        try {
            console.log(items);


            const rawResponse = await fetch('/buy_items', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    totalPrice: totalPriceField,
                    itemList: items
                }),
            });

            if (!rawResponse.ok) {
                // Handle non-200 responses
                const errorText = await rawResponse.text();
                console.error('Server error response:', errorText);
                return;
            }

            const content = await rawResponse.json();
            console.log('Server response after removal:', content);
        } catch (error) {
            console.error('Error removing item:', error);
        }
    });
}
