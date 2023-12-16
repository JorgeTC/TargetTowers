document.addEventListener("DOMContentLoaded", function () {
    const COLUMNS = 3;
    const HEIGHT = 4;
    const NUMBER_OF_BALLS = initNumberOfBalls(COLUMNS, HEIGHT);
    const COLORS = initializeColors(NUMBER_OF_BALLS);

    let selectedPiece = null;

    let state = initializeState(COLORS, COLUMNS, HEIGHT);

    const referenceState = initializeState(COLORS, COLUMNS, HEIGHT);

    function initializeColors(colorsLength) {
        const colors_list = [];
        for (let i = 0; i < colorsLength; i++) {
            colors_list.push(hslToHex(i * (360 / colorsLength) % 360, 100, 50));
        }
        shuffle(colors_list);
        return colors_list;
    }

    function initNumberOfBalls(columns, height) {
        const minBalls = columns * 2;
        const maxBalls = columns * height / 2 + 1;
        return randomIntFromInterval(minBalls, maxBalls);
    }

    function randomIntFromInterval(min, max) { // min and max included 
        return Math.floor(Math.random() * (max - min + 1) + min)
    }

    function shuffle(array) {
        // While there remain elements to shuffle.
        for (let currentIndex = 1; currentIndex < array.length; currentIndex++) {

            // Pick a remaining element.
            let randomIndex = Math.floor(Math.random() * currentIndex);

            // And swap it with the current element.
            [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
        }

        return array;
    }

    function hslToHex(h, s, l) {
        l /= 100;
        const a = s * Math.min(l, 1 - l) / 100;
        const f = n => {
            const k = (n + h / 30) % 12;
            const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
            return Math.round(255 * color).toString(16).padStart(2, '0');
        };
        return `#${f(0)}${f(8)}${f(4)}`;
    }

    function chooseBallsInColumn(columns, balls, height) {
        if (balls / columns > height)
            throw new Error("Cannot hold all the balls");

        if (columns === 1) {
            return [balls];
        }

        const possibilities = Array.from(Array(Math.min(height, balls) + 1).keys());
        shuffle(possibilities)
        for (const firstColumnBalls of possibilities) {
            try {
                return [firstColumnBalls, ...chooseBallsInColumn(columns - 1, balls - firstColumnBalls, height)];
            }
            catch (error) {
                continue;
            }
        }
    }

    function generatePythonCode(state, elements) {
        const codeLines = state.map(column => `[${column.map(value => value === null || elements.indexOf(value) === -1 ? 'None' : elements.indexOf(value)).join(', ')}]`);
        const pythonCode = `State([${codeLines.join(',\n                       ')}])`;
        console.log(pythonCode);
    }

    function initializeState(elements, columns, height) {

        const shuffleElements = [...elements]
        shuffle(shuffleElements)

        const ballsInColumns = chooseBallsInColumn(columns, elements.length, height);
        // Initialize empty array
        const initialState = [];
        let colorIndex = 0;
        for (const columnLength of ballsInColumns) {
            const column = [];

            for (let j = 0; j < height; j++) {
                // Colorize the elements of this column
                // When we get too high the color is null.
                const isColoredPiece = (j < columnLength);
                if (isColoredPiece) {
                    column.push(shuffleElements[colorIndex]);
                    colorIndex++;
                }
                else {
                    column.push(null);
                }
            }
            initialState.push(column);
        }

        generatePythonCode(initialState, elements);

        return initialState;
    }

    function renderInteractiveTowers() {
        const gameContainer = document.getElementById("game-container");
        gameContainer.innerHTML = "";

        if (haveWon())
            gameContainer.classList.add("game-container-won");
        else
            gameContainer.classList.remove("game-container-won");

        state.forEach((column, columnIndex) => {
            const columnDiv = document.createElement("div");
            columnDiv.classList.add("column");

            column.forEach((color, rowIndex) => {
                const pieceDiv = document.createElement("div");
                pieceDiv.classList.add("piece");

                if (color !== null) {
                    pieceDiv.style.backgroundColor = color;
                }
                pieceDiv.addEventListener("click", () => handleClick(columnIndex));

                // Give the current piece a selected style
                if (selectedPiece && columnIndex === selectedPiece.column && rowIndex === selectedPiece.row) {
                    pieceDiv.classList.add("selected");
                }
                columnDiv.appendChild(pieceDiv);
            });

            gameContainer.appendChild(columnDiv);
        });
    }

    function renderReferenceTowers() {
        // Render the reference state
        const referenceGameContainer = document.getElementById("reference-game-container");
        referenceGameContainer.innerHTML = "";

        for (const column of referenceState) {
            const columnDiv = document.createElement("div");
            columnDiv.classList.add("column");

            for (const color of column) {
                const pieceDiv = document.createElement("div");
                pieceDiv.classList.add("piece");
                pieceDiv.style.backgroundColor = color;
                columnDiv.appendChild(pieceDiv);
            }

            referenceGameContainer.appendChild(columnDiv);
        }
    }

    function renderGame() {
        renderInteractiveTowers();
        renderReferenceTowers();
    }

    function handleFirstClick(columnIndex) {
        const rowTopPiece = findTopPiece(columnIndex);
        if (rowTopPiece === -1) {
            selectedPiece = null;
        }
        else {
            selectedPiece = { column: columnIndex, row: rowTopPiece };
        }
    }

    function handleSecondClick(columnIndex) {
        // Second click: move the piece
        const targetColumn = columnIndex;
        if (targetColumn === selectedPiece.column) {
            selectedPiece = null;
            return;
        }
        const targetRow = findEmptyRow(targetColumn);

        if (targetRow !== -1) {
            // Move the piece
            state[targetColumn][targetRow] = state[selectedPiece.column][selectedPiece.row];
            state[selectedPiece.column][selectedPiece.row] = null;

            generatePythonCode(state, COLORS)
        }

        // Reset the selected piece after the move
        selectedPiece = null;
    }

    function haveWon() {
        for (let i = 0; i < COLUMNS; i++) {
            for (let j = 0; j < HEIGHT; j++) {
                if (state[i][j] !== referenceState[i][j])
                    return false;
            }
        }
        return true;
    }

    function handleClick(columnIndex) {
        if (selectedPiece === null) {
            handleFirstClick(columnIndex);
        } else {
            handleSecondClick(columnIndex);
        }

        // Update the game display
        renderGame();
    }

    function findEmptyRow(columnIndex) {
        // First elements of the column will store the pieces
        // I need to search from bottom to top
        for (let i = 0; i <= HEIGHT; i++) {
            if (state[columnIndex][i] === null) {
                return i;
            }
        }
        return -1; // No empty row found
    }

    function findTopPiece(columnIndex) {
        // Last elements of the column will have the empty spaces
        // I need to search from top to bottom
        for (let i = HEIGHT - 1; i >= 0; i--) {
            if (state[columnIndex][i] !== null) {
                return i;
            }
        }
        return -1; // No empty row found
    }

    renderGame();
});
