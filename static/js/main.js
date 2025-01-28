document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const questionInput = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatHistory = document.getElementById('chatHistory');
    const summaryBtn = document.getElementById('summaryBtn');
    const compareBtn = document.getElementById('compareBtn');
    const faqBtn = document.getElementById('faqBtn');
    const apiKeyModal = document.getElementById('apiKeyModal');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const saveApiKey = document.getElementById('saveApiKey');
    const apiKeyStatus = document.getElementById('api-key-status');

    // Check for API key on load
    checkApiKey();

    // Event Listeners
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary-color)';
    });
    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border-color)';
    });
    dropZone.addEventListener('drop', handleFileDrop);
    fileInput.addEventListener('change', handleFileSelect);
    sendBtn.addEventListener('click', handleQuestion);
    summaryBtn.addEventListener('click', generateSummary);
    compareBtn.addEventListener('click', compareDocument);
    faqBtn.addEventListener('click', generateFAQ);
    saveApiKey.addEventListener('click', saveApiKeyHandler);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleQuestion();
    });

    // Functions
    async function checkApiKey() {
        try {
            const response = await fetch('/check-api-key');
            const data = await response.json();
            
            if (!data.hasKey) {
                apiKeyModal.style.display = 'block';
                apiKeyStatus.innerHTML = '⚠️ API Key niet ingesteld';
            } else {
                apiKeyStatus.innerHTML = '✅ API Key ingesteld';
            }
        } catch (error) {
            console.error('Error checking API key:', error);
            apiKeyStatus.innerHTML = '❌ Error bij controleren API key';
        }
    }

    async function saveApiKeyHandler() {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) return;

        try {
            const response = await fetch('/set-api-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            });

            if (response.ok) {
                apiKeyModal.style.display = 'none';
                apiKeyStatus.innerHTML = '✅ API Key ingesteld';
                apiKeyInput.value = '';
            }
        } catch (error) {
            console.error('Error saving API key:', error);
        }
    }

    async function handleFileDrop(e) {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border-color)';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            await uploadFile(file);
        }
    }

    async function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file && file.type === 'application/pdf') {
            await uploadFile(file);
        }
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        showProcessingIndicator();

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                enableInterface();
                addMessage('Bot', 'Document succesvol geüpload en verwerkt. Stel gerust uw vragen!');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            addMessage('Bot', 'Er is een fout opgetreden bij het uploaden van het document.');
        } finally {
            hideProcessingIndicator();
        }
    }

    async function handleQuestion() {
        const question = questionInput.value.trim();
        if (!question) return;

        addMessage('User', question);
        questionInput.value = '';

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await response.json();
            addMessage('Bot', data.answer);
        } catch (error) {
            console.error('Error asking question:', error);
            addMessage('Bot', 'Er is een fout opgetreden bij het verwerken van uw vraag.');
        }
    }

    async function generateSummary() {
        try {
            const response = await fetch('/summarize');
            const data = await response.json();
            addMessage('Bot', 'Samenvatting: ' + data.summary);
        } catch (error) {
            console.error('Error generating summary:', error);
            addMessage('Bot', 'Er is een fout opgetreden bij het genereren van de samenvatting.');
        }
    }

    async function generateFAQ() {
        try {
            const response = await fetch('/generate-faq');
            const data = await response.json();
            addMessage('Bot', 'Veelgestelde vragen:\n' + data.faq);
        } catch (error) {
            console.error('Error generating FAQ:', error);
            addMessage('Bot', 'Er is een fout opgetreden bij het genereren van de FAQ.');
        }
    }

    async function compareDocument() {
        // Implement document comparison functionality
        console.log('Document comparison not implemented yet');
    }

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender.toLowerCase()}-message`;
        messageDiv.textContent = text;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function showProcessingIndicator() {
        const indicator = document.querySelector('.processing-indicator');
        indicator.hidden = false;
    }

    function hideProcessingIndicator() {
        const indicator = document.querySelector('.processing-indicator');
        indicator.hidden = true;
    }

    function enableInterface() {
        questionInput.disabled = false;
        sendBtn.disabled = false;
        summaryBtn.disabled = false;
        compareBtn.disabled = false;
        faqBtn.disabled = false;
    }
});