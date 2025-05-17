// JavaScript for the UI frontend

const pdfListUl = document.getElementById('pdf-list');
const pdfInput = document.getElementById('pdf-input');
const modelSelect = document.getElementById('model-select');
const totalTokensSpan = document.getElementById('total-tokens');
const todayTokensSpan = document.getElementById('today-tokens');
const logOutputTextarea = document.getElementById('log-output');
const startStopButton = document.getElementById('start-stop-button');
const stateStatusDiv = document.getElementById('state-status');

let currentPdfSources = [];
let uiState = 'configuring'; // 'configuring' or 'listening'

// Function called by Python to set the initial state
function setInitialState(state) {
    console.log("JS: Received initial state:", state);
    currentPdfSources = state.pdfSources || [];
    populatePdfList();

    const availableModels = state.availableModels || [];
    populateModelSelect(availableModels, state.selectedModel);

    updateTokenDisplay(state.tokenUsage.total, state.tokenUsage.daily[getTodayDateString()] || 0);

    // Set initial UI state based on how the app starts (likely configuring initially)
    // setUIState('configuring'); // Assuming it starts in configuring mode
    // If main.py starts in listening mode, it should call setUIState after webview.start()
}

// Function called by Python to update the UI state
function setUIState(state) {
    console.log("JS: Setting UI state to:", state);
    uiState = state;
    document.body.classList.remove('configuring-state', 'listening-state');
    document.body.classList.add(state + '-state');

    stateStatusDiv.textContent = state === 'configuring' ? 'Configuring' : 'Listening (Hotkeys Active)';
    stateStatusDiv.className = 'status ' + state; // Update classes for styling

    startStopButton.textContent = state === 'configuring' ? 'Start Listening' : 'Stop Listening';
    startStopButton.classList.remove('configuring', 'listening');
    startStopButton.classList.add(state);

    // Disable/enable input fields and buttons based on state
    const inputs = document.querySelectorAll('#pdf-section input, #pdf-section button, #model-section select');
    inputs.forEach(input => {
        input.disabled = state === 'listening';
    });
}


// --- PDF List Management ---
function populatePdfList() {
    pdfListUl.innerHTML = ''; // Clear current list
    currentPdfSources.forEach((source, index) => {
        const li = document.createElement('li');
        li.textContent = source;
        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Remove';
        removeBtn.className = 'remove-btn';
        removeBtn.onclick = () => removePdfSource(index);
        li.appendChild(removeBtn);
        pdfListUl.appendChild(li);
    });
}

function addPdfSource() {
    const source = pdfInput.value.trim();
    if (source && !currentPdfSources.includes(source)) {
        currentPdfSources.push(source);
        populatePdfList();
        pdfInput.value = '';
        // Inform Python about the updated list
        window.pywebview.api.setPdfSources(currentPdfSources);
    } else if (source) {
        console.log("JS: PDF source already in the list.");
    }
}

function removePdfSource(index) {
    if (index >= 0 && index < currentPdfSources.length) {
        currentPdfSources.splice(index, 1);
        populatePdfList();
        // Inform Python about the updated list
        window.pywebview.api.setPdfSources(currentPdfSources);
    }
}

// Allow adding PDF source by pressing Enter in the input field
pdfInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent default form submission if applicable
        addPdfSource();
    }
});


// --- Model Selection ---
function populateModelSelect(models, selectedModel) {
    modelSelect.innerHTML = ''; // Clear current options
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        if (model === selectedModel) {
            option.selected = true;
        }
        modelSelect.appendChild(option);
    });
}

modelSelect.addEventListener('change', function() {
    const selectedModel = modelSelect.value;
    console.log("JS: Selected model:", selectedModel);
    // Inform Python about the selected model
    window.pywebview.api.setSelectedModel(selectedModel);
});


// --- Token Usage Display ---
function updateTokenDisplay(total, today) {
    totalTokensSpan.textContent = total;
    todayTokensSpan.textContent = today;
}

function getTodayDateString() {
    const today = new Date();
    const year = today.getFullYear();
    const month = (today.getMonth() + 1).toString().padStart(2, '0');
    const day = today.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}


// --- Log Display ---
// Function called by Python to append a log line
function appendLog(logLine) {
    logOutputTextarea.value += logLine;
    // Auto-scroll to the bottom
    logOutputTextarea.scrollTop = logOutputTextarea.scrollHeight;
}


// --- Start/Stop Listening Control ---
function toggleListening() {
    startStopButton.disabled = true; // Prevent double clicks

    if (uiState === 'configuring') {
        console.log("JS: Calling Python startListening()");
        window.pywebview.api.startListening().then(() => {
             // Python's startListening will call setUIState on success
             startStopButton.disabled = false;
        }).catch(error => {
             console.error("JS: Error calling startListening:", error);
             appendLog(`Error starting listening: ${error}\n`);
             startStopButton.disabled = false; // Re-enable button on error
        });
    } else if (uiState === 'listening') {
        console.log("JS: Calling Python stopListening()");
         window.pywebview.api.stopListening().then(() => {
             // Python's stopListening will call setUIState on success
             startStopButton.disabled = false;
         }).catch(error => {
             console.error("JS: Error calling stopListening:", error);
             appendLog(`Error stopping listening: ${error}\n`);
             startStopButton.disabled = false; // Re-enable button on error
         });
    }
}

// --- Initial State Sync (Called by Python after window is shown) ---
// The function `setInitialState` is called from Python's `_on_window_shown` callback.
// This ensures the DOM is ready before we try to populate elements.

// --- Handle window close ---
// webview.start() handles the GUI event loop. When the user closes the window,
// webview fires a 'closed' event. In ui.py, we've hooked this event to call
// the main script's quitApp callback (set_quitting_flag).
// The TrayIcon's quit menu also calls set_quitting_flag.

// --- Initial UI Setup ---
// The initial UI state is 'configuring' by default, but main.py will call setInitialState
// and potentially setUIState to reflect the actual application state.
setUIState('configuring'); // Set initial visual state until Python overrides