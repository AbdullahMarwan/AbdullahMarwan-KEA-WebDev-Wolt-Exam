// Initialize the map
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
        { coords: [55.6845, 12.5641], popup: "Marker 1: Nørrebro" },
        { coords: [55.6886, 12.5529], popup: "Marker 2: Superkilen Park" },
        { coords: [55.6922, 12.5425], popup: "Marker 3: Assistens Cemetery" },
        { coords: [55.6833, 12.5589], popup: "Marker 4: Mændenes Hjem (Men's Home)" },
        { coords: [55.6819, 12.5538], popup: "Marker 5: Nørrebro Station" },
      ];

  //Loop through the markerLocations array and add markers to the map
  markerLocations.forEach(function (location) {
    var marker = L.marker(location.coords).addTo(map);
    marker.bindPopup(location.popup);
  });


}
setTimeout(test, 3000);