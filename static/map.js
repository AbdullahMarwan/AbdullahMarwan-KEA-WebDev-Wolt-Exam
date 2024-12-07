// // This function is responsible for initializing the map and adding markers
// function initMap() {
//   // Initialize the map
//   var map = L.map("map").setView([55.6845, 12.5641], 15);

//   // Add OpenStreetMap tile layer
//   L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
//       maxZoom: 20,
//       attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
//   }).addTo(map);

//   // Define the bounds for the area (e.g., Nørrebro, Copenhagen)
//   var bounds = L.latLngBounds([55.6500, 12.5100], [55.7100, 12.6200]);

//   // Restrict map's view to the defined bounds
//   map.setMaxBounds(bounds);
//   map.options.maxZoom = 20;
//   map.options.minZoom = 15;

// //   // Fetch the restaurant data from the API
// //   fetch('/api/restaurants')
// //       .then(response => response.json())  // Parse the JSON response
// //       .then(restaurants => {
// //           console.log('Restaurants:', restaurants);  // Debugging output
// //           if (restaurants && restaurants.length > 0) {
// //               addMarkers(restaurants, map, bounds);  // Function to add markers to the map
// //               displayRestaurantList(restaurants);  // Display restaurants in a list
// //           } else {
// //               console.error('No restaurant data available.');
// //           }
// //       })
// //       .catch(error => {
// //           console.error("Error fetching restaurants:", error);
// //       });
// // }

// // Function to add markers to the map
// function addMarkers(restaurants, map, bounds) {
//   restaurants.forEach(function(restaurant) {
//       // Create a marker with random coordinates (for demo purposes)
//       const randomCoords = generateRandomCoordinates(bounds);
//       const marker = L.marker(randomCoords).addTo(map);
//       marker.bindPopup(`<b>${restaurant.user_name}</b><br>ID: ${restaurant.user_pk}`);
//   });
// }

// // Function to generate random coordinates
// function generateRandomCoordinates(bounds) {
//   const latSpan = bounds.getNorthEast().lat - bounds.getSouthWest().lat;
//   const lngSpan = bounds.getNorthEast().lng - bounds.getSouthWest().lng;
//   const randomLat = bounds.getSouthWest().lat + Math.random() * latSpan;
//   const randomLng = bounds.getSouthWest().lng + Math.random() * lngSpan;
//   return [randomLat, randomLng];
// }

// // Function to display restaurants in a list
// function displayRestaurantList(restaurants) {
//   const listContainer = document.getElementById('restaurant-list');
//   restaurants.forEach(function(restaurant) {
//       const li = document.createElement('li');
//       li.textContent = `${restaurant.user_name} (ID: ${restaurant.user_pk})`;
//       listContainer.appendChild(li);
//   });
// }

// // Initialize the map after the document is loaded
// document.addEventListener('DOMContentLoaded', function() {
//   initMap();
// });
