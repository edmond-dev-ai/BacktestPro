// renderer.js - Final version that loads data from the cloud bot.

// --- DOM Element References ---
const chartContainer = document.getElementById('chart-container');
const loadingSpinner = document.getElementById('loading-spinner');
// ... other DOM references

// --- Global State ---
let chart;
let candleSeries;
let masterData = null; // Cache the data

// --- Chart Initialization ---
function initializeChart() {
    if (chart) return;
    chart = LightweightCharts.createChart(chartContainer, { /* ... chart options ... */ });
    candleSeries = chart.addCandlestickSeries({ /* ... series options ... */ });
    new ResizeObserver(() => chart && chart.resize(chartContainer.clientWidth, chartContainer.clientHeight)).observe(chartContainer);
    chart.subscribeCrosshairMove(updateOhlcOverlay);
}

// --- Data Loading Logic ---
async function initializeAppData() {
    console.log('Attempting to download data from cloud bot...');
    loadingSpinner.style.display = 'block';

    try {
        const csvData = await window.electronAPI.getChartData();
        
        if (csvData) {
            masterData = csvData;
            const parsedData = parseCsvData(csvData);
            candleSeries.setData(parsedData);
            chart.timeScale().fitContent();
            console.log('Successfully loaded and displayed chart data.');
        } else {
            throw new Error("Could not fetch data.");
        }

    } catch (error) {
        console.error('Fatal error during app initialization:', error);
        alert(`Error: ${error.message}`);
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

// Helper to parse the CSV data
function parseCsvData(csv) {
    return Papa.parse(csv, { header: true, dynamicTyping: true, skipEmptyLines: true })
        .data.map(row => ({
            time: new Date(row.time).getTime() / 1000, // Convert to UTC timestamp
            open: row.open,
            high: row.high,
            low: row.low,
            close: row.close,
        }));
}

// --- UI Interactivity ---
function updateOhlcOverlay(param) { /* ... same as before ... */ }
// timeframeButtons logic needs to be updated for intraday data later

// --- App Entry Point ---
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    initializeAppData();
});
