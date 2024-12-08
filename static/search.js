document.getElementById("search-items").addEventListener("input", function () {
    const query = this.value.trim();
    const resultsContainer = document.getElementById("item-results");

    if (query.length > 0) {
        console.log(`Searching for items: ${query}`);
        fetch(`/api/search-items?q=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((data) => {
                resultsContainer.innerHTML = ""; // Clear previous results
                if (data.items.length > 0) {
                    resultsContainer.style.display = "block"; // Show results dropdown
                    data.items.forEach((item) => {
                        const itemElement = document.createElement("div");
                        itemElement.className = "search-result-item";
                        itemElement.innerHTML = `<strong>${item.item_title}</strong> - $${item.item_price}`;
                        resultsContainer.appendChild(itemElement);
                    });
                } else {
                    resultsContainer.style.display = "block";
                    resultsContainer.innerHTML = "<p>No items found.</p>";
                }
            })
            .catch((error) => console.error("Error fetching item results:", error));
    } else {
        resultsContainer.style.display = "none";
        resultsContainer.innerHTML = "";
    }
});

document.getElementById("search-restaurants").addEventListener("input", function () {
    const query = this.value.trim();
    const resultsContainer = document.getElementById("restaurant-results");

    if (query.length > 0) {
        console.log(`Searching for restaurants: ${query}`);
        fetch(`/api/search-restaurants?q=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((data) => {
                resultsContainer.innerHTML = ""; // Clear previous results
                if (data.restaurants.length > 0) {
                    resultsContainer.style.display = "block"; // Show results dropdown
                    data.restaurants.forEach((restaurant) => {
                        const itemElement = document.createElement("div");
                        itemElement.className = "search-result-item";
                        itemElement.innerHTML = `<strong>${restaurant.user_name}</strong>`;
                        resultsContainer.appendChild(itemElement);
                    });
                } else {
                    resultsContainer.style.display = "block";
                    resultsContainer.innerHTML = "<p>No restaurants found.</p>";
                }
            })
            .catch((error) => console.error("Error fetching restaurant results:", error));
    } else {
        resultsContainer.style.display = "none";
        resultsContainer.innerHTML = "";
    }
});

// Prevent form submission on "Enter" key press for both search inputs
document.querySelectorAll('.search-container input').forEach(input => {
    input.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent the default action (page reload)
        }
    });
});

// Function to close dropdown when clicking outside
document.addEventListener("click", function(event) {
    const searchItemsInput = document.getElementById('search-items');
    const searchRestaurantsInput = document.getElementById('search-restaurants');
    const itemResults = document.getElementById('item-results');
    const restaurantResults = document.getElementById('restaurant-results');

    if (!searchItemsInput.contains(event.target) && !itemResults.contains(event.target)) {
        itemResults.style.display = "none"; // Hide item results dropdown
    }

    if (!searchRestaurantsInput.contains(event.target) && !restaurantResults.contains(event.target)) {
        restaurantResults.style.display = "none"; // Hide restaurant results dropdown
    }
});
