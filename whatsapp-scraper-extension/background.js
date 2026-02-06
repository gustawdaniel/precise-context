chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'runScraper') {
      chrome.scripting.executeScript({
          target: { tabId: sender.tab.id },
          files: ['contentScript.js']
      });
  }
});
