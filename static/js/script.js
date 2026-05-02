document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('email-text');
    const charCount = document.querySelector('.char-count');
    const analyzeBtn = document.getElementById('analyze-btn');
    const clearBtn = document.getElementById('clear-btn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.querySelector('.btn-loader');
    const resultContainer = document.getElementById('result-container');
    const resultLabel = document.getElementById('result-label');
    const resultIcon = document.getElementById('result-icon');
    const confidenceValue = document.getElementById('confidence-value');
    const progressFill = document.getElementById('progress-fill');

    // Update character count
    textarea.addEventListener('input', () => {
        charCount.textContent = `${textarea.value.length} characters`;
    });

    // Clear content
    clearBtn.addEventListener('click', () => {
        textarea.value = '';
        charCount.textContent = '0 characters';
        resultContainer.classList.add('hidden');
        textarea.focus();
    });

    // Analyze Logic
    analyzeBtn.addEventListener('click', async () => {
        const text = textarea.value.trim();
        
        if (!text) {
            alert('Please paste some email content first!');
            return;
        }

        // Show loading state
        analyzeBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        resultContainer.classList.add('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                displayResult(data.label, data.confidence);
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('Something went wrong connecting to the AI engine.');
        } finally {
            // Restore button state
            analyzeBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
        }
    });

    function displayResult(label, confidence) {
        resultContainer.classList.remove('hidden');
        
        const isSpam = label.toLowerCase() === 'spam';
        
        // Set content
        resultLabel.textContent = `Result: This is likely ${label.toUpperCase()}`;
        resultLabel.style.color = isSpam ? 'var(--danger)' : 'var(--accent)';
        
        // Set icon
        resultIcon.className = `result-icon-wrapper ${isSpam ? 'result-icon-spam' : 'result-icon-ham'}`;
        resultIcon.innerHTML = isSpam ? '<i class="fas fa-virus"></i>' : '<i class="fas fa-check-double"></i>';
        
        // Set confidence and progress
        confidenceValue.textContent = `${confidence}%`;
        
        // Reset and then animate progress bar
        progressFill.className = `progress-fill ${isSpam ? 'bg-spam' : 'bg-ham'}`;
        progressFill.style.width = '0%';
        
        setTimeout(() => {
            progressFill.style.width = `${confidence}%`;
        }, 100);

        // Smooth scroll to result
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});
