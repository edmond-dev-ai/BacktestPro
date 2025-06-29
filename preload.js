// preload.js - A simplified version for testing.

const { contextBridge, ipcRenderer } = require('electron');

// We only need to expose the test function for this diagnostic.
contextBridge.exposeInMainWorld('electronAPI', {
  runTest: () => ipcRenderer.invoke('run-test'),
});
