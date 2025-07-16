document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-upload');
    const resultsDiv = document.getElementById('results');

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData();
        formData.append('image', imageInput.files[0]);

        try {
            // Show loading state
            resultsDiv.innerHTML = `
                <h2>Processing...</h2>
                <p>Detecting and analyzing underlined words...</p>
            `;

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                resultsDiv.innerHTML = `
                    <h2>Error</h2>
                    <p class="error">${data.error}</p>
                `;
            } else {
                let resultsHTML = '<h2>Detected Words and Definitions:</h2>';
                
                if (data.words && data.words.length > 0) {
                    resultsHTML += '<div class="word-list">';
                    data.words.forEach(wordData => {
                        resultsHTML += `
                            <div class="word-item">
                                <h3 class="word">${wordData.word}</h3>
                        `;

                        if (wordData.definition_data.success) {
                            wordData.definition_data.meanings.forEach(meaning => {
                                resultsHTML += `
                                    <div class="meaning">
                                        <p class="part-of-speech">${meaning.part_of_speech}</p>
                                        <ol class="definitions">
                                            ${meaning.definitions.map(def => `<li>${def}</li>`).join('')}
                                        </ol>
                                    </div>
                                `;
                            });
                        } else {
                            resultsHTML += `
                                <p class="error">
                                    ${wordData.definition_data.error || 'Could not find definition'}
                                </p>
                            `;
                        }

                        resultsHTML += '</div>';
                    });
                    resultsHTML += '</div>';
                } else {
                    resultsHTML += `
                        <p class="no-results">No underlined words were detected in the image.</p>
                        <p>Try uploading a different image or make sure the words are clearly underlined.</p>
                    `;
                }
                
                resultsDiv.innerHTML = resultsHTML;
            }

        } catch (error) {
            console.error('Error:', error);
            resultsDiv.innerHTML = `
                <h2>Error</h2>
                <p class="error">An error occurred while processing your image: ${error.message}</p>
            `;
        }
    });
});