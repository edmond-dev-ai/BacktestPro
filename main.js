// main.js - A simplified version for testing the API connection.

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');
const crypto = require('crypto');

// --- Configuration ---
const QC_USER_ID = '386333';
const QC_API_TOKEN = 'c65a1873cb3039acc5b76def3ec5614f097a30da0cc23b41be169abdc2866603';
const QC_PROJECT_ID = '28418589';

// --- Main Window Creation ---
function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadFile('index.html');
  mainWindow.webContents.openDevTools();
}

// --- Application Lifecycle ---
app.whenReady().then(() => {
    createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// --- API Test Function ---
async function runAPITest() {
    try {
        console.log("--- STARTING API TEST ---");
        const url = `https://www.quantconnect.com/api/v2/object-store/read`;
        const simpleApiKey = 'test_key.txt'; // The simple key we are testing

        const timestamp = Math.floor(Date.now() / 1000).toString();
        const timeStampedToken = `${QC_API_TOKEN}:${timestamp}`;
        const hashedToken = crypto.createHash('sha256').update(timeStampedToken, 'utf8').digest('hex');
        const authString = `${QC_USER_ID}:${hashedToken}`;
        const authBase64 = Buffer.from(authString).toString('base64');

        const headers = {
            'Authorization': `Basic ${authBase64}`,
            'Timestamp': timestamp
        };
        
        const params = {
            projectId: QC_PROJECT_ID,
            key: simpleApiKey
        };

        console.log(`Requesting URL via GET: ${url} for key: ${simpleApiKey}`);
        
        const response = await axios.get(url, { params, headers, timeout: 30000 });
        
        console.log("--- TEST RESULT ---");
        if (response.data.success) {
            console.log("SUCCESS! The server found the file.");
            console.log("File Content:", response.data.data);
            return { success: true, content: response.data.data };
        } else {
            console.log("FAILURE! The server responded but the call was not successful.");
            console.log("Errors:", response.data.errors);
            return { success: false, errors: response.data.errors };
        }

    } catch (error) {
        console.log("--- TEST FAILED ---");
        if (error.response) {
            console.error(`FAILURE! Server responded with status: ${error.response.status}`);
        } else {
            console.error("FAILURE! A network error occurred:", error.message);
        }
        return { success: false, error: error.message };
    }
}

// When the UI is ready, it will invoke this handler.
ipcMain.handle('run-test', runAPITest);
