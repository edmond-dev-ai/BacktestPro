// renderer.js - A simplified version for testing.

// When the HTML document is fully loaded, call the test function in the main process.
document.addEventListener('DOMContentLoaded', () => {
    console.log("UI Loaded. Requesting API test from main process...");
    // Call the 'runTest' function that we exposed in preload.js
    window.electronAPI.runTest();
});
