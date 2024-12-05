const diaryEntries = [
    { name: "Brescia", aliases: ["BrexaJ"], column: 51, text: "Da poi disnar, fo Gran Consejo. Fato elecfion di  podestà di Brexa, tolto sier Piero da Pexaro fo cao  di X, sier Mann Sanudo fo savio a Terra ferma,  sier Francesco da Pexaro V avc^dor extraordina-  rio et sier Hironimo Barbaro dotor el cavalier fo  di la Zonla et niun passò. E di Pregadi achadete che  tolti quatro, sier MichicI Memo fo di la Zonta passò  ma bave 9 balote in tutto il corpo di più di lì altri,  et riratte dal conto, non vien a passar di una balota  per la leze in Regina a carte 107, presa dil 1472 a  di 13 Aprii, et però non fo stridalo. Rimaxe le altre  voxe poste. "},
    { name: "Bologna", aliases: ["ItalU"], column: 646, text: "Di MUan, di Alvise Mar..." },
    { name: "Bologna", aliases: ["ItalU"], column: 646, text: "Di MUan, di Alvise Mar..." },

    { name: "Bologna", aliases: ["ItalU"], column: 646, text: "Di MUan, di Alvise Mar..." },
    { name: "Bologna", aliases: ["ItalU"], column: 646, text: "Di MUan, di Alvise Mar..." },
    { name: "Bologna", aliases: ["ItalU"], column: 646, text: "Di MUan, di Alvise Mar..." },
    { name: "Bologna", aliases: ["ItalU"], column: 646, text: "Di MUan, di Alvise Mar..." },
    { name: "Bologna", aliases: ["ItalU"], column: 646, text: "Di MUan, di Alvise Mar..." },

    // Add more entries as per your CSV
];

let currentPage = 0;
const entriesPerPage = 7;

function loadIndex() {
    const list = document.getElementById('placeList');
    const startIndex = currentPage * entriesPerPage;
    const endIndex = Math.min(startIndex + entriesPerPage, diaryEntries.length);
    
    list.innerHTML = ""; // Clear previous list

    for (let i = startIndex; i < endIndex; i++) {
        const entry = diaryEntries[i];
        const listItem = document.createElement('li');
        listItem.innerHTML = `${entry.name} (${entry.aliases.join(", ")})`;
        listItem.onclick = () => displayEntry(entry);
        list.appendChild(listItem);
    }

    document.getElementById('prevButton').disabled = currentPage === 0;
    document.getElementById('nextButton').disabled = currentPage >= Math.floor(diaryEntries.length / entriesPerPage);
}

function changePage(direction) {
    currentPage += direction;
    loadIndex();
}

function searchPlace() {
    const searchQuery = document.getElementById('searchBox').value.toLowerCase();
    const filteredEntries = diaryEntries.filter(entry => 
        entry.name.toLowerCase().includes(searchQuery) || entry.aliases.some(alias => alias.toLowerCase().includes(searchQuery))
    );
    displayIndex(filteredEntries);
}

function displayIndex(entries) {
    const list = document.getElementById('placeList');
    list.innerHTML = "";
    entries.forEach(entry => {
        const listItem = document.createElement('li');
        listItem.textContent = entry.name;
        listItem.onclick = () => displayEntry(entry);
        list.appendChild(listItem);
    });
}

function displayEntry(entry) {
    const leftColumn = document.getElementById('columnLeft');
    const rightColumn = document.getElementById('columnRight');
    const infoTable = document.getElementById('infoTable');
    const columnNumberDisplay = document.getElementById('columnNumber'); // Column number display

    // Set the column number at the top to show current | current+1
    columnNumberDisplay.textContent = `Column Number: ${entry.column} | ${entry.column + 1}`;

    // Split text into two columns
    const columns = splitText(entry.text);
    leftColumn.innerHTML = columns[0];
    rightColumn.innerHTML = columns[1];

    // Highlight place name in the text
    highlightText(entry, leftColumn);
    highlightText(entry, rightColumn);

    // Update related information (e.g., character names)
    updateInfoTable(entry);
}


function splitText(text) {
    const mid = Math.floor(text.length / 2);
    return [text.substring(0, mid), text.substring(mid)];
}

// Highlight place name in the text
function highlightText(entry, column) {
    const namesToHighlight = [entry.name, ...entry.aliases]; // Ensure aliases are also highlighted
    namesToHighlight.forEach(placeName => {
        const regex = new RegExp(`(${placeName})`, 'gi');
        column.innerHTML = column.innerHTML.replace(regex, '<span class="highlight">$1</span>');
    });
}

function updateInfoTable(entry) {
    const infoTable = document.getElementById('infoTable');
    infoTable.innerHTML = "<tr><th>Character</th><th>Details</th></tr>";
    
    entry.text.match(/sier \w+/g)?.forEach(character => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${character}</td><td>Details about ${character}</td>`;
        infoTable.appendChild(row);
    });
}

loadIndex();
