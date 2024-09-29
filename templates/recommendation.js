document.addEventListener('DOMContentLoaded', function () {
    const recommendationsList = document.getElementById('recommendations-list');
    const backButton = document.getElementById('back-button');

    // Clear the recommendations list before fetching new data
    recommendationsList.innerHTML = '<p>Loading recommendations...</p>';

    // Fetch recommendations from the server (update the URL as needed)
    fetch('/recommendations')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Clear the loading message
            recommendationsList.innerHTML = '';

            // Check if data is in the expected format
            if (Array.isArray(data) && data.length > 0) {
                data.forEach(song => {
                    const songDiv = document.createElement('div');
                    songDiv.className = 'song-item';
                    songDiv.innerHTML = `
                        <h3>${song.name} by ${song.artist}</h3>
                        <a href="${song.url}" target="_blank">Listen on Spotify</a>
                    `;
                    recommendationsList.appendChild(songDiv);
                });
            } else {
                recommendationsList.innerHTML = '<p>No recommendations available.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            recommendationsList.innerHTML = '<p>Failed to load recommendations. Please try again later.</p>';
        });

    // Back button action
    backButton.addEventListener('click', () => {
        window.location.href = '/'; // Redirect to home
    });
});
