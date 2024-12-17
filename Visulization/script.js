document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners to the navigation buttons
    document.getElementById('nextParagraph').addEventListener('click', nextParagraph);
    document.getElementById('prevParagraph').addEventListener('click', prevParagraph);
});
 
// Function to send the text to the backend for name extraction
 

let diaryEntries = [];
let currentPage = 0;
const entriesPerPage = 7;
let filteredEntries = []; // Keep track of filtered entries for search
const searchBox = document.getElementById('searchBox');
searchBox.addEventListener('keyup', searchPlace);
let maxPage = 0
let currentPlaceIndex = -1; // Initialize with a default value (-1 means no place selected)
let currentColumnIndex = 0;  // Initially, the first column (0th index) of the current place

async function loadCSV() {
    try {
        const response = await fetch('../name_paragraph_match_results.csv');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
        diaryEntries = processCSV(csvText);
        filteredEntries = diaryEntries; // Initially, no filtering
        loadIndex(); // Load the index after processing the data
        maxPage = Math.ceil(diaryEntries.length / entriesPerPage); // Corrected to calculate maxPage correctly
    } catch (error) {
        console.error('Error loading CSV file:', error);
    }
}


// Process the CSV text into structured data
function processCSV(csvText) {
    const rows = csvText.trim().split('\n').slice(1); // Remove header row

    const processedEntries = {};

    rows.forEach(row => {
        // Split the row by commas, and handle improperly quoted fields
        const columns = row.match(/(?:[^,"]+|"[^"]*")+/g);

        if (columns.length < 4) {
            console.error("Skipping invalid row:", row);
            return;
        }

        let placeNamesString = columns[1].replace(/'/g, '"').trim();

        // Fix any missing or mismatched quotes
        if (placeNamesString.startsWith('"') && placeNamesString.endsWith('"')) {
            placeNamesString = placeNamesString.slice(1, -1);  // Remove surrounding quotes
        }

        // Ensure it's a valid JSON array
        if (!placeNamesString.startsWith('[') || !placeNamesString.endsWith(']')) {
            console.error('Invalid format for place names:', placeNamesString);
            return;
        }

        let placeNames;
        try {
            placeNames = JSON.parse(placeNamesString);
        } catch (error) {
            console.error('Error parsing place names:', placeNamesString, error);
            return;
        }

        const columnNumber = parseInt(columns[2], 10);
        let paragraph = columns[3].replace(/^"|"$/g, '');  // Remove surrounding quotes

        // Clean up the paragraph content
        paragraph = cleanUpParagraph(paragraph);

        const mainPlace = placeNames[0];  // Only store the first place as the main name

        if (!processedEntries[mainPlace]) {
            processedEntries[mainPlace] = { columns: [], text: [], alternatives: [] };
        }

        if (!processedEntries[mainPlace].columns.includes(columnNumber)) {
            processedEntries[mainPlace].columns.push(columnNumber);
        }

        // Store the cleaned paragraph content
        processedEntries[mainPlace].text.push([columnNumber, paragraph]);

        // Store alternative place names
        const alternativeNames = placeNames.slice(1);
        processedEntries[mainPlace].alternatives.push(...alternativeNames);
    });

    // Convert the processed entries into a proper array format
    const entries = Object.entries(processedEntries).map(([name, { columns, text, alternatives }]) => ({
        name,
        columns,
        text,
        alternatives: [...new Set(alternatives)], // Remove duplicates
    }));
    // console.log(entries);
    return entries;
}

// Clean up the paragraph to remove unwanted quotes and line breaks
function cleanUpParagraph(paragraph) {
    // Remove unwanted double quotes and line breaks
    paragraph = paragraph.replace(/"\s*$/, '');  // Remove trailing double quotes
    paragraph = paragraph.replace(/(\r\n|\n|\r)/g, ' ');  // Replace line breaks with spaces

    // Optional: remove any stray characters or extra spaces
    paragraph = paragraph.replace(/\s+/g, ' ').trim();  // Normalize spaces

    return paragraph;
}



// Load and display the index
function loadIndex() {
    const list = document.getElementById('placeList');
    const startIndex = currentPage * entriesPerPage;
    const endIndex = Math.min(startIndex + entriesPerPage, filteredEntries.length);

    list.innerHTML = ""; // Clear previous list

    for (let i = startIndex; i < endIndex; i++) {
        const entry = filteredEntries[i];

        const listItem = document.createElement('li');
        listItem.textContent = entry.name;
        listItem.onclick = () => displayPlace(entry.name); // Pass the name of the place here
        list.appendChild(listItem);
    }

    // Disable/Enable navigation buttons
    document.getElementById('prevButton').disabled = currentPage === 0;
    document.getElementById('nextButton').disabled = currentPage >= Math.floor(filteredEntries.length / entriesPerPage);
}


// Navigate between pages
function changePage(direction) {
    currentPage += direction;
    loadIndex();
}

// Search for a place
function searchPlace() {
    const searchQuery = document.getElementById('searchBox').value.toLowerCase();
    filteredEntries = diaryEntries.filter(entry =>
        entry.name.toLowerCase().includes(searchQuery)
    );
    currentPage = 0; // Reset to the first page
    loadIndex(); // Update the index list with filtered entries
}


// When a place is selected, initialize column navigation
function displayPlace(placeName) {
    const place = diaryEntries.find(entry => entry.name === placeName);  // Change `entries` to `diaryEntries`
    if (!place) {
        console.error('Place not found:', placeName);
        return;
    }

    currentPlace = place;
    currentColumnIndex = 0; // Start at the first column of the selected place
    updatePlaceContent(); // Display the content for the first column of the selected place
    updateInfoTable();
    // Ensure the column is available before trying to highlight
    const column = document.getElementById("column"); // Make sure you reference the right column element
    if (column) {
        highlightText(place, column); // Highlight names in the displayed column content
    } else {
        console.error("Column element not found!");
    }
    // Update current place name in the info section
    document.getElementById('currentPlaceName').innerText = `${place.name}`;
}

// Update content for the current column of the selected place
function updatePlaceContent() {
    const placeName = currentPlace.name; // Current place name
    const columnNumber = currentPlace.columns[currentColumnIndex]; // The current column number

    const content = getColumnContent(placeName, columnNumber);

    // Update the content displayed on the page
    const columnContentElement = document.getElementById('column');
    if (columnContentElement) {
        columnContentElement.innerText = content;
        document.getElementById('currentColumn').innerText = `Column Number: ${columnNumber}`;
    } else {
        console.error('Column element not found.');
    }

    updateNavigationButtons();
    updateInfoTable();

    const place = diaryEntries.find(entry => entry.name === placeName);  // Change `entries` to `diaryEntries`
    // Ensure the column is available before trying to highlight
    const column = document.getElementById("column"); // Make sure you reference the right column element
    if (column) {
        highlightText(place, column); // Highlight names in the displayed column content
    } else {
        console.error("Column element not found!");
    }
}

// Get the content for the specified column of a place
function getColumnContent(placeName, columnNumber) {
    const place = diaryEntries.find(entry => entry.name === placeName);  // Change `entries` to `diaryEntries`

    if (!place) {
        return "No content available for this column."; // If place not found
    }

    const columnContent = place.text.filter(item => item[0] === columnNumber);

    if (columnContent.length > 0) {
        // Combine all paragraphs for the given column into a single string
        return columnContent.map(item => item[1]).join(' ');
    } else {
        return "No content available for this column."; // If no content for this column
    }
}

// Navigate to the next column
function nextParagraph() {
    if (currentColumnIndex < currentPlace.columns.length - 1) {
        currentColumnIndex++; // Move to the next column index
        updatePlaceContent(); // Update the displayed content
    }
}

// Navigate to the previous column
function prevParagraph() {
    if (currentColumnIndex > 0) {
        currentColumnIndex--; // Move to the previous column index
        updatePlaceContent(); // Update the displayed content
    }
}

// Update the state of the navigation buttons (enable/disable)
function updateNavigationButtons() {
    const prevButton = document.getElementById('prevParagraph');
    const nextButton = document.getElementById('nextParagraph');

    // Disable the previous button if we're at the first column for this place
    prevButton.disabled = currentColumnIndex <= 0;

    // Disable the next button if we're at the last column for this place
    nextButton.disabled = currentColumnIndex >= currentPlace.columns.length - 1;
}


function attachNavigationHandlers(entry) {
    const prevButton = document.getElementById('prevParagraph');
    const nextButton = document.getElementById('nextParagraph');
    // Clear existing event listeners
    prevButton.onclick = null;
    nextButton.onclick = null;

    // Attach new handlers for current entry
    prevButton.onclick = () => {
        if (currentPlaceIndex > 0) {
            currentPlaceIndex--;
            updatePlaceContent(entry);
        }
    };

    nextButton.onclick = () => {
        if (currentPlaceIndex < entry.columns.length - 1) {
            currentPlaceIndex++;
            updatePlaceContent(entry);
        }
    };
}


// Attach event listeners
document.getElementById('prevParagraph').addEventListener('click', () => {
    if (currentPlaceIndex > 0) {
        currentPlaceIndex--;
        const entry = filteredEntries[currentPage]; // Get the current entry
        updatePlaceContent(entry);
    }
});

document.getElementById('nextParagraph').addEventListener('click', () => {
    if (currentPlaceIndex < filteredEntries[currentPage].columns.length - 1) {
        currentPlaceIndex++;
        const entry = filteredEntries[currentPage]; // Get the current entry
        updatePlaceContent(entry);
    }
});


// Reattach event listeners for paragraph navigation buttons
document.getElementById('prevParagraph').onclick = () => {
    if (currentPlaceIndex > 0) {
        currentPlaceIndex--;
        updatePlaceContent(filteredEntries[currentPage]);
    }
};

document.getElementById('nextParagraph').onclick = () => {
    if (currentPlaceIndex < filteredEntries[currentPage].columns.length - 1) {
        currentPlaceIndex++;
        updatePlaceContent(filteredEntries[currentPage]);
    }
};

function highlightText(entry, column) {
    // Check if entry.name exists
    if (!entry.name) {
        console.error('Entry name is missing');
        return;
    }

    // Ensure entry.alternatives is always an array (which holds aliases)
    const aliases = Array.isArray(entry.alternatives) ? entry.alternatives : (entry.alternatives ? [entry.alternatives] : []);
    

    // Escape special characters for regex matching
    function escapeRegExp(str) {
        return str.replace(/[.*+?^=!:${}()|\[\]\/\\]/g, '\\$&'); // escape all special characters
    }

    // Combine name and aliases into one array and escape them for regex
    const namesAndAliases = [entry.name, ...aliases].map(escapeRegExp).join('|');
    console.log("Regex pattern:", namesAndAliases);

    const regex = new RegExp(`(${namesAndAliases})`, 'gi'); // 'gi' for global and case-insensitive matching

    // Ensure the column has content
    if (!column.innerHTML) {
        console.error('Column content is empty');
        return;
    }

    // Highlight the matched names/aliases in the column
    const originalContent = column.innerHTML;
    const highlightedContent = originalContent.replace(regex, '<span class="highlight">$1</span>');

    // Only update the column if the content has changed (i.e., if something was highlighted)
    if (originalContent !== highlightedContent) {
        column.innerHTML = highlightedContent;
    } else {
    }
}


// Update related information table
function updateInfoTable() {
    const infoTable = document.getElementById('infoTable');
    infoTable.innerHTML = "<tr><th>Character</th></tr>"; // Clear previous table content

    // Extract the content for the current column
    const currentColumnNumber = currentPlace.columns[currentColumnIndex];
    const currentColumnContent = currentPlace.text.find(item => item[0] === currentColumnNumber);

    if (currentColumnContent) {
        // Get the paragraph text of the current column
        const columnText = currentColumnContent[1];

        // Match 'sier' followed by one or more words (including accented characters and spaces)
        const characters = columnText.match(/sier\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*)/g);

        if (characters) {
            // Process each match to only keep the first two words after 'sier'
            const uniqueCharacters = new Set(
                characters.map(character => {
                    const name = character.replace(/^sier\s+/i, ''); // Remove 'sier ' from the matched string
                    const nameParts = name.split(' '); // Split the name into parts

                    // Keep only the first two words of the name
                    const nameToShow = nameParts.slice(0, 2).join(' ');

                    return nameToShow;
                })
            );

            uniqueCharacters.forEach(character => {
                const row = document.createElement('tr');
                row.innerHTML = `<td class="character-row">•     ${character}</td>`; // Only the character name
                infoTable.appendChild(row);
            });
        }
    }
}





// Load the CSV data on page load
loadCSV();
// });
