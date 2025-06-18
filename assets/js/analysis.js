document.addEventListener('DOMContentLoaded', function () {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileInput');
    const previewArea = document.getElementById('preview-area');
    const filePreviewContainer = document.getElementById('file-preview-container');
    const analyzeBtn = document.getElementById('analyze-btn');
    const clearBtn = document.getElementById('clear-btn');
    const analysisResults = document.getElementById('analysis-results');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    const maxSize = 50 * 1024 * 1024; // 50MB

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.style.borderColor = '#3498db', false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.style.borderColor = '#ccc', false);
    });

    dropArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleDrop(e) {
        handleFiles(e.dataTransfer.files);
    }

    function handleFiles(files) {
        filePreviewContainer.innerHTML = '';
        previewArea.style.display = 'block';
        analyzeBtn.disabled = false;
        clearBtn.disabled = false;

        [...files].forEach(file => {
            if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
                alert("Unsupported file format.");
                return;
            }

            if (file.size > maxSize) {
                alert("File too large. Maximum size is 50MB.");
                return;
            }

            const wrapper = document.createElement('div');
            wrapper.className = 'file-preview';

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.style.maxWidth = '150px';
                img.style.borderRadius = '5px';
                const reader = new FileReader();
                reader.onload = e => img.src = e.target.result;
                reader.readAsDataURL(file);
                wrapper.appendChild(img);
            } else {
                const video = document.createElement('video');
                video.style.maxWidth = '150px';
                video.controls = true;
                const source = document.createElement('source');
                source.src = URL.createObjectURL(file);
                source.type = file.type;
                video.appendChild(source);
                wrapper.appendChild(video);
            }

            filePreviewContainer.appendChild(wrapper);
        });
    }

    analyzeBtn.addEventListener('click', async function () {
        analyzeBtn.disabled = true;
        progressContainer.style.display = 'block';
        progressText.textContent = "Uploading...";
        progressBar.style.width = "0%";

        const formData = new FormData();
        [...fileInput.files].forEach(file => formData.append("files", file));

        try {
            // Simulate progress
            for (let i = 0; i <= 100; i += 20) {
                progressBar.style.width = i + "%";
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            progressText.textContent = "Analyzing...";

            // Use relative URL for fetch
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            progressContainer.style.display = 'none';
            analysisResults.style.display = 'block';

            // Process the response and display the media
            if (result.results && result.results.length > 0) {
                const firstResult = result.results[0];
                let outputHTML = `<p>${firstResult.status}</p>`;
                if (firstResult.processed_file) {
                    // Append timestamp to bypass caching

                    ///////////////////
                    // Assume firstResult.processed_file is something like "video.mp4"
                    const baseFileURL = firstResult.processed_file; 
                    const fileExtension = baseFileURL.split('.').pop().toLowerCase();

                    // Append a timestamp to bypass caching.
                    const fileURL = baseFileURL + '?t=' + Date.now();

                    if (['mp4', 'mov'].includes(fileExtension)) {
                        const mimeType = fileExtension === 'mov' ? 'video/quicktime' : 'video/mp4';
                        outputHTML += `<video controls preload="metadata" playsinline muted style="max-width:300px;">
                                        <source src="${fileURL}" type="${mimeType}">
                                        Your browser does not support the video tag.
                                    </video>`;
                    } else {
                        outputHTML += `<img src="${fileURL}" alt="Processed result image" style="max-width:300px;">`;
                    }

                    
                }
                document.querySelector('.results-container').innerHTML = outputHTML;
            } else {
                document.querySelector('.results-container').innerHTML = `<p>No results returned.</p>`;
            }
        } catch (error) {
            alert("Error analyzing files. Please try again.");
            console.error(error);
        }

        analyzeBtn.disabled = false;
    });

    clearBtn.addEventListener('click', function () {
        fileInput.value = '';
        filePreviewContainer.innerHTML = '';
        previewArea.style.display = 'none';
        analysisResults.style.display = 'none';
        analyzeBtn.disabled = true;
        clearBtn.disabled = true;
        progressContainer.style.display = 'none';
    });
});
