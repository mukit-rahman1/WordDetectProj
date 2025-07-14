document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const resultsDiv = document.getElementById('results');

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData();
        formData.append('image', imageInput.files[0]);

        try {
            resultsDiv.innerHTML = 'Processing image...'; // Indicate processing

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                let resultsHTML = '<h2>Detected Words and Definitions:</h2><ul>';
                if (data.definitions && data.definitions.length > 0) {
                    data.definitions.forEach(item => {
                        resultsHTML += `<li><strong>${item.word}:</strong> ${item.definition || 'Definition not found.'}</li>`;
                    });
                } else {
                    resultsHTML += '<li>No underlined words found or definitions retrieved.</li>';
                }
                resultsHTML += '</ul>';
                resultsDiv.innerHTML = resultsHTML;
            }

        } catch (error) {
            console.error('Error uploading image:', error);
            resultsDiv.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
        }
    });
});