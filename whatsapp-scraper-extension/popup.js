document.getElementById('runScraper').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];

        // Check if the URL is not a chrome:// URL or other restricted URL
        if (activeTab.url.startsWith('chrome://') || activeTab.url.startsWith('https://chrome.google.com/webstore') || activeTab.url.startsWith('https://chrome.google.com/extensions')) {
            alert('Please open WhatsApp Web first. This extension can only run on WhatsApp Web.');
            return;
        }

        // Set a timeout to check if the scraper starts
        const timeout = setTimeout(() => {
            displayRefreshMessage();
        }, 5000); // 5 seconds timeout

        chrome.scripting.executeScript({
            target: { tabId: activeTab.id },
            files: ['contentScript.js']
        }, () => {
            // Clear the timeout if the script executes successfully
            clearTimeout(timeout);
        });
    });
});

function displayRefreshMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.id = 'refreshMessage';
    messageDiv.innerHTML = `
        The scraper did not start. Please refresh the page and try again.
        <button id="refreshButton">Refresh</button>
    `;
    document.body.appendChild(messageDiv);

    document.getElementById('refreshButton').addEventListener('click', () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.reload(tabs[0].id);
            document.body.removeChild(messageDiv);
        });
    });
}
