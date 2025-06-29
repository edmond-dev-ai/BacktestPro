// main.js - Final version that fetches data from the public GitHub URL.

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');
const { spawn } = require('child_process');

// --- Configuration ---
const GITHUB_USERNAME = "edmond-dev-ai"; // Your GitHub Username
const REPO_NAME = "BacktestPro";      // Your GitHub Repository Name
const DATA_FILE = "data/SPY_1minute_data.csv";
// This is the public URL where your data will be stored.
const DATA_URL = `https://cdn.jsdelivr.net/gh/${GITHUB_USERNAME}/${REPO_NAME}@latest/${DATA_FILE}`;

// --- Main Window Creation ---
function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1600,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadFile('index.html');
  mainWindow.webContents.openDevTools();
}

// --- Application Lifecycle ---
app.whenReady().then(createWindow);
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });


// --- IPC Handlers ---

// This handler now downloads the data from the public jsDelivr URL.
ipcMain.handle('get-chart-data', async () => {
  try {
    console.log(`Fetching data from public URL: ${DATA_URL}`);
    // Use axios to download the CSV file content as text.
    const response = await axios.get(DATA_URL, { timeout: 60000 }); // 60 second timeout
    console.log("Data downloaded successfully from GitHub.");
    return response.data; // The raw CSV text
  } catch (error) {
    console.error("Failed to download data from GitHub:", error.message);
    throw new Error("Could not download data file from the cloud. The cloud bot may not have run yet.");
  }
});

// The resampling handler stays the same.
ipcMain.handle('resample-data', async (event, dailyCsvData, timeframe) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['resampler.py', timeframe]);
    let resultData = '';
    let errorData = '';
    pythonProcess.stdout.on('data', (data) => { resultData += data.toString(); });
    pythonProcess.stderr.on('data', (data) => { errorData += data.toString(); });
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve(JSON.parse(resultData));
      } else {
        reject(new Error(`Python script exited with code ${code}`));
      }
    });
    pythonProcess.stdin.write(dailyCsvData);
    pythonProcess.stdin.end();
  });
});
