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

function syncKeywordUI() {
    renderMultiSelectUI({
        selectEl: document.getElementById("keyword"),
        containerEl: document.getElementById("keywordMulti")
    });
}

function syncSubcategoryUI() {
    renderMultiSelectUI({
        selectEl: document.getElementById("subcategory"),
        containerEl: document.getElementById("subcategoryMulti")
    });
}

document.getElementById("keyword").addEventListener("change", function () {
    const selectedKeywords = getSelectedValues(this);
    renderSubcategoriesForKeywords(selectedKeywords);
    syncKeywordUI();
    syncSubcategoryUI();
});

document.getElementById("subcategory").addEventListener("change", function () {
    syncSubcategoryUI();
});

function populateKeywords(data) {
    // Update subcategoryMap with fetched data
    subcategoryMap = {};
    Object.keys(data).forEach(keyword => {
        // Normalize keyword to lowercase for consistency
        const normalizedKey = keyword.toLowerCase();
        subcategoryMap[normalizedKey] = data[keyword];
    });

    // Populate keyword select dropdown
    const keywordSelect = document.getElementById("keyword");
    keywordSelect.innerHTML = "";
    
    Object.keys(data).forEach(keyword => {
        const option = document.createElement("option");
        option.value = keyword.toLowerCase();
        option.text = keyword;
        keywordSelect.appendChild(option);
    });

    // Initialize UI with fetched data
    const subcategorySelect = document.getElementById("subcategory");
    renderSubcategoriesForKeywords(getSelectedValues(keywordSelect));
    syncKeywordUI();
    syncSubcategoryUI();

    // If no keywords selected, default-select first keyword for nicer UX
    if (getSelectedValues(keywordSelect).length === 0 && keywordSelect.options.length > 0) {
        setSelectedValues(keywordSelect, [keywordSelect.options[0].value]);
    }
    // If still no subcategories (e.g. map empty), just render UI
    if (subcategorySelect.options.length === 0) syncSubcategoryUI();
}

// Fetch metadata on page load
fetch("/metadata")
    .then(res => res.json())
    .then(data => populateKeywords(data))
    .catch(error => {
        console.error("Error fetching metadata:", error);
        // Fallback to empty state if fetch fails
        populateKeywords({});
    });

function generate() {
    const keyword = getSelectedValues(document.getElementById("keyword"));
    const subcategory = getSelectedValues(document.getElementById("subcategory"));
    const query = document.getElementById("query").value;

    fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            keyword,
            subcategory,
            query
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("response").innerText =
            JSON.stringify(data, null, 2);
    });
}

function showIngest() {
    document.getElementById("ingestSection").style.display = "block";
}

function ingest() {
    // Allow comma-separated keywords/subcategories in ingest fields
    const keyword = document.getElementById("newKeyword").value
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);

    const subcategory = document.getElementById("newSubcategory").value
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);

    const content = document.getElementById("newContent").value;

    fetch("/ingest", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            keyword,
            subcategory,
            content
        })
    })
    .then(res => res.json())
    .then(data => {
        alert("Knowledge stored (mock): " + data.status);
    });
}

