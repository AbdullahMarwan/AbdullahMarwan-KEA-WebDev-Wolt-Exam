document.getElementById("search-query").addEventListener("input", function () {
    const query = this.value.trim();
    const resultsContainer = document.getElementById("search-results");

    if (query.length > 0) {
        console.log(`Searching for: ${query}`);
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then((response) => {
                console.log("Response received:", response);
                return response.json();
            })
            .then((data) => {
                console.log("Search results:", data);
                resultsContainer.innerHTML = ""; // Clear previous results

                if (data.items.length > 0) {
                    resultsContainer.style.display = "block"; // Show the results dropdown
                    data.items.forEach((item) => {
                        const itemElement = document.createElement("div");
                        itemElement.className = "search-result-item";
                        itemElement.innerHTML = `
                            <strong>${item.item_title}</strong> - $${item.item_price}
                        `;
                        resultsContainer.appendChild(itemElement);
                    });
                } else {
                    resultsContainer.style.display = "block"; // Show the results dropdown
                    resultsContainer.innerHTML = "<p>No items found.</p>";
                }
            })
            .catch((error) => {
                console.error("Error fetching search results:", error);
            });
    } else {
        resultsContainer.style.display = "none"; // Hide the dropdown if there's no query
        resultsContainer.innerHTML = ""; // Clear results if the query is empty
    }
});
