let subcategoryMap = {};

function getSelectedValues(selectEl) {
    return Array.from(selectEl.selectedOptions).map(o => o.value).filter(Boolean);
}

function setSelectedValues(selectEl, values) {
    const set = new Set(values);
    Array.from(selectEl.options).forEach(opt => {
        opt.selected = set.has(opt.value);
    });
    selectEl.dispatchEvent(new Event("change"));
}

function renderSubcategoriesForKeywords(selectedKeywords) {
    const subcategorySelect = document.getElementById("subcategory");

    const previousSelection = new Set(getSelectedValues(subcategorySelect));
    subcategorySelect.innerHTML = "";

    const merged = new Set();
    selectedKeywords.forEach(k => {
        // Handle both normalized (lowercase) and original case keys
        const normalizedKey = k.toLowerCase();
        const subcategories = subcategoryMap[normalizedKey] || subcategoryMap[k] || [];
        subcategories.forEach(sub => merged.add(sub));
    });

    Array.from(merged).sort().forEach(sub => {
        const option = document.createElement("option");
        option.value = sub;
        option.text = sub;
        if (previousSelection.has(sub)) option.selected = true;
        subcategorySelect.appendChild(option);
    });
}

function renderMultiSelectUI({ selectEl, containerEl }) {
    const selected = new Set(getSelectedValues(selectEl));
    containerEl.innerHTML = "";

    const chips = document.createElement("div");
    chips.className = "chips";

    const optionsWrap = document.createElement("div");
    optionsWrap.className = "options";

    Array.from(selectEl.options).forEach(opt => {
        const value = opt.value;
        const text = opt.text;

        const row = document.createElement("label");
        row.className = "option";

        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.checked = selected.has(value);
        cb.addEventListener("change", () => {
            opt.selected = cb.checked;
            selectEl.dispatchEvent(new Event("change"));
        });

        const span = document.createElement("span");
        span.className = "label";
        span.textContent = text;

        row.appendChild(cb);
        row.appendChild(span);
        optionsWrap.appendChild(row);

        if (selected.has(value)) {
            const chip = document.createElement("span");
            chip.className = "chip";
            chip.textContent = text;

            const x = document.createElement("button");
            x.type = "button";
            x.setAttribute("aria-label", `Remove ${text}`);
            x.textContent = "×";
            x.addEventListener("click", () => {
                opt.selected = false;
                selectEl.dispatchEvent(new Event("change"));
            });

            chip.appendChild(x);
            chips.appendChild(chip);
        }
    });

    if (chips.childElementCount === 0) {
        const empty = document.createElement("div");
        empty.className = "hint";
        empty.textContent = "Select one or more options below.";
        chips.appendChild(empty);
    }

    containerEl.appendChild(chips);
    containerEl.appendChild(optionsWrap);
}


// Load keywords/subcategories on start
fetch("/api/keywords")
    .then(r => r.json())
    .then(data => {
        const keywordSelect = document.getElementById("keyword");
        const subcategorySelect = document.getElementById("subcategory");

        // Populate keywords
        Object.keys(data).sort().forEach(k => {
            const opt = document.createElement("option");
            opt.value = k;
            opt.text = k;
            keywordSelect.appendChild(opt);
        });

        // Save map
        subcategoryMap = data;

        // Setup Keyword Multi-Select
        const keywordMultiContainer = document.getElementById("keywordMulti");
        renderMultiSelectUI({ selectEl: keywordSelect, containerEl: keywordMultiContainer });

        // Listen for changes on native select to re-render custom UI + update subcategories
        keywordSelect.addEventListener("change", () => {
            renderMultiSelectUI({ selectEl: keywordSelect, containerEl: keywordMultiContainer });
            const selected = getSelectedValues(keywordSelect);
            renderSubcategoriesForKeywords(selected);
        });

        // Setup Subcategory Multi-Select (initially empty, but we set up listener)
        const subcategoryMultiContainer = document.getElementById("subcategoryMulti");
        renderMultiSelectUI({ selectEl: subcategorySelect, containerEl: subcategoryMultiContainer });

        subcategorySelect.addEventListener("change", () => {
            renderMultiSelectUI({ selectEl: subcategorySelect, containerEl: subcategoryMultiContainer });
        });
    });

function showIngest() {
    const section = document.getElementById("ingestSection");
    if (section) {
        section.classList.toggle("active");
    }
}

function ingest() {
    const text = document.getElementById("knowledgeBase").value;
    if (!text.trim()) {
        showDialog("Error", "Knowledge base content is empty.", true);
        return;
    }

    fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
    .then(r => r.json())
    .then(data => {
        showDialog("Success", "Knowledge base updated.");
        // Reload keywords/subcategories to reflect new data
        // For simplicity, just reload page or re-fetch.
        // Let's re-fetch keywords logic if we want dynamic update, 
        // but simple reload might be easier or just let user know.
    })
    .catch(err => {
        console.error(err);
        showDialog("Error", "Failed to save knowledge.", true);
    });
}

function generate() {
    const keywordSelect = document.getElementById("keyword");
    const subcategorySelect = document.getElementById("subcategory");
    const query = document.getElementById("query").value;
    
    const keywords = getSelectedValues(keywordSelect);
    const subcategories = getSelectedValues(subcategorySelect);

    if (keywords.length === 0) {
        showDialog("Validation Error", "Please select at least one Keyword.", true);
        return;
    }

    const btn = document.querySelector(".btn-primary");
    const originalText = btn.textContent;
    btn.textContent = "Generating...";
    btn.disabled = true;

    const responsePre = document.getElementById("response");
    responsePre.textContent = "Generating...";

    fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            query: query,
            keywords: keywords,
            subcategories: subcategories
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            responsePre.textContent = "Error: " + data.error;
        } else {
            responsePre.textContent = data.response;
        }
    })
    .catch(err => {
        console.error(err);
        responsePre.textContent = "Error occurred while generating.";
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

function exportTestCases() {
    const query = document.getElementById("query").value;
    const keywordSelect = document.getElementById("keyword");
    const subcategorySelect = document.getElementById("subcategory");
    
    const keywords = getSelectedValues(keywordSelect);
    const subcategories = getSelectedValues(subcategorySelect);

    fetch("/export", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            query: query,
            keywords: keywords,
            subcategories: subcategories
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.file) {
            // Trigger file download
            window.location.href = `/download?file=${encodeURIComponent(data.file)}`;
        } else {
            showDialog("Export Failed", "No file returned.", true);
        }
    })
    .catch(error => {
        console.error("Export error:", error);
        showDialog("Export Error", "An error occurred while exporting test cases.", true);
    });
}

function showDialog(title, message, isError = false) {
    const dialog = document.createElement("div");
    dialog.className = "dialog-overlay";
    dialog.innerHTML = `
        <div class="dialog ${isError ? "error" : ""}">
            <h3>${title}</h3>
            <p>${message}</p>
            <button onclick="this.closest('.dialog-overlay').remove()">OK</button>
        </div>
    `;
    document.body.appendChild(dialog);
}

// Help Modal Functions
function showHelp() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeHelp() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close help modal when clicking outside or pressing Escape
const helpModal = document.getElementById('helpModal');
if (helpModal) {
    helpModal.addEventListener('click', function(e) {
        if (e.target === this) {
            closeHelp();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeHelp();
        }
    });
}
