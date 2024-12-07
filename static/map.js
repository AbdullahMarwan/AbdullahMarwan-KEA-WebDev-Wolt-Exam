document.addEventListener("DOMContentLoaded", function () {
  // Initialize the map
  var map = L.map("map").setView([55.6845, 12.5641], 15);

  // Add OpenStreetMap tile layer
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 20,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // Fetch restaurant data from Flask API
  fetch("/api/restaurants")
      .then((response) => response.json())
      .then((restaurants) => {
          restaurants.forEach((restaurant) => {
              // Add markers to the map
              L.marker([restaurant.lat, restaurant.lon])
                  .addTo(map)
                  .bindPopup(`<a href="/customer/items/${restaurant.user_pk}">${restaurant.user_name}</a>`);
          });
      })
      .catch((error) => console.error("Error fetching restaurant data:", error));
});