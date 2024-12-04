
// Initialize the map
var map = L.map("map").setView([55.6845, 12.564148], 15);

// Add OpenStreetMap tile layer
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
maxZoom: 20,
attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// Define the bounds for the area (e.g., Nørrebro, Copenhagen)
var bounds = L.latLngBounds(
  [55.6500, 12.5100], // South-West corner
  [55.7100, 12.6200]  // North-East corner
);

// Restrict map's view to the defined bounds
map.setMaxBounds(bounds);

// Optionally, ensure that the map doesn't zoom out beyond a specific level
map.options.maxZoom = 20;  // Maximum zoom level
map.options.minZoom = 15;   // Minimum zoom level (adjust as needed)

function test() {
    var markerLocations = [
        { coords: [55.6845, 12.5641], popup: "Restaurant 1: Manfreds" },
        { coords: [55.6880, 12.5495], popup: "Restaurant 2: Relæ" },
        { coords: [55.6890, 12.5530], popup: "Restaurant 3: The Coffee Collective" },
        { coords: [55.6815, 12.5573], popup: "Restaurant 4: Nørrebro Bryghus" },
        { coords: [55.6925, 12.5418], popup: "Restaurant 5: La Banchina" },
        { coords: [55.6842, 12.5598], popup: "Restaurant 6: Marv & Ben" },
        { coords: [55.6878, 12.5605], popup: "Restaurant 7: Pizzeria Mamemi" },
        { coords: [55.6897, 12.5505], popup: "Restaurant 8: Bistro Lupa" },
        { coords: [55.6851, 12.5490], popup: "Restaurant 9: Grød" },
        { coords: [55.6812, 12.5550], popup: "Restaurant 10: The Laundromat Cafe" }
];

  //Loop through the markerLocations array and add markers to the map
markerLocations.forEach(function (location) {
    var marker = L.marker(location.coords).addTo(map);
    marker.bindPopup(location.popup);
});

}
setTimeout(test, 3000);