import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 설정
st.set_page_config(page_title="Vibe Block Tetris Pro+", layout="centered")

# 전체 게임 로직 (HTML + CSS + JS)
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Noto Sans KR', sans-serif; 
            background: #f0f9ff; 
            color: #1e293b; 
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        .grid-cell { width: 45px; height: 45px; border: 1px solid rgba(0,0,0,0.03); transition: all 0.2s; }
        .block-active { border-radius: 8px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); }
        .preview-item { cursor: grab; transition: transform 0.1s; }
        .preview-item:active { cursor: grabbing; }
        .score-font { font-family: 'Orbitron', sans-serif; }
        .board-container { box-shadow: 0 20px 50px rgba(0,0,0,0.08); background: white; padding: 12px; border-radius: 24px; position: relative; }
        .dragging { opacity: 0.4; }

        /* 콤보 텍스트 애니메이션 */
        @keyframes combo-up {
            0% { transform: scale(0.5); opacity: 0; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(1); opacity: 0; }
        }
        .combo-effect {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3rem;
            font-weight: 900;
            color: #4f46e5;
            text-shadow: 2px 2px 10px rgba(255,255,255,0.8);
            pointer-events: none;
            z-index: 50;
            animation: combo-up 0.8s ease-out forwards;
            display: none;
        }
    </style>
</head>
<body>

    <!-- 콤보 효과 출력용 디브 -->
    <div id="combo-text" class="combo-effect">GREAT!</div>

    <div class="mb-6 text-center">
        <h1 class="text-4xl font-bold mb-2 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent score-font uppercase tracking-tighter">Block Tetris Pro+</h1>
        <div class="flex gap-10 justify-center items-center mt-4">
            <div class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Score <p id="score" class="text-3xl text-slate-800 score-font">0</p></div>
            <div class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Best <p id="best-score" class="text-3xl text-indigo-500 score-font">0</p></div>
        </div>
    </div>

    <div id="board" class="board-container mb-8">
        <div id="grid-container" class="grid grid-cols-8 gap-1"></div>
    </div>

    <div id="previews" class="flex justify-around items-center w-full max-w-md bg-white/70 backdrop-blur-md p-6 rounded-[2.5rem] border border-white shadow-xl min-h-[160px]"></div>

    <script>
        const BOARD_SIZE = 8;
        const CELL_SIZE = 45;
        let score = 0;
        let bestScore = localStorage.getItem('vibeTetrisBestPlus') || 0;
        let boardState = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
        
        // 블록 가짓수 확장 (기본 7종 + 대형 L, 십자가, 징검다리 등 총 10종)
        const SHAPES = [
            [[1,1,1,1]], [[1,1],[1,1]], [[1,1,1],[0,1,0]], 
            [[1,0],[1,0],[1,1]], [[1,1,1]], [[1]], [[1,1]],
            [[1,1,1],[1,0,0],[1,0,0]], // 대형 L
            [[0,1,0],[1,1,1],[0,1,0]], // 십자가
            [[1,0,1],[1,1,1]]          // U자형
        ];
        const COLORS = ['#38bdf8', '#3b82f6', '#6366f1', '#8b5cf6', '#d946ef', '#f43f5e', '#f59e0b', '#10b981', '#f97316', '#64748b'];

        const gridContainer = document.getElementById('grid-container');
        const previewsEl = document.getElementById('previews');
        const comboEl = document.getElementById('combo-text');

        function initBoard() {
            gridContainer.innerHTML = '';
            for (let r = 0; r < BOARD_SIZE; r++) {
                for (let c = 0; c < BOARD_SIZE; c++) {
                    const cell = document.createElement('div');
                    cell.className = 'grid-cell bg-slate-50 rounded-lg';
                    cell.id = `cell-${r}-${c}`;
                    gridContainer.appendChild(cell);
                }
            }
            document.getElementById('best-score').innerText = bestScore;
        }

        function generatePreviews() {
            previewsEl.innerHTML = '';
            for (let i = 0; i < 3; i++) {
                const shapeIdx = Math.floor(Math.random() * SHAPES.length);
                const color = COLORS[shapeIdx];
                const shape = SHAPES[shapeIdx];
                const container = document.createElement('div');
                container.className = 'preview-item';
                container.draggable = true;
                const grid = document.createElement('div');
                grid.style.display = 'grid';
                grid.style.gridTemplateColumns = `repeat(${shape[0].length}, ${CELL_SIZE}px)`;
                grid.style.gap = '4px';

                shape.forEach(row => {
                    row.forEach(cellVal => {
                        const div = document.createElement('div');
                        div.style.width = `${CELL_SIZE}px`; div.style.height = `${CELL_SIZE}px`;
                        if(cellVal) { div.style.backgroundColor = color; div.className = 'rounded-md shadow-sm'; }
                        grid.appendChild(div);
                    });
                });
                container.appendChild(grid);
                previewsEl.appendChild(container);

                container.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('shapeIdx', shapeIdx);
                    e.dataTransfer.setData('previewIdx', i);
                    e.dataTransfer.setData('offsetX', e.offsetX);
                    e.dataTransfer.setData('offsetY', e.offsetY);
                    setTimeout(() => container.classList.add('dragging'), 0);
                });
                container.addEventListener('dragend', () => container.classList.remove('dragging'));
            }
        }

        gridContainer.addEventListener('dragover', (e) => e.preventDefault());
        gridContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            const shapeIdx = e.dataTransfer.getData('shapeIdx');
            const previewIdx = e.dataTransfer.getData('previewIdx');
            const offX = parseInt(e.dataTransfer.getData('offsetX'));
            const offY = parseInt(e.dataTransfer.getData('offsetY'));
            const shape = SHAPES[shapeIdx];
            const rect = gridContainer.getBoundingClientRect();
            
            const mouseX = e.clientX - rect.left - offX;
            const mouseY = e.clientY - rect.top - offY;
            const c = Math.round(mouseX / (CELL_SIZE + 4));
            const r = Math.round(mouseY / (CELL_SIZE + 4));

            if (canPlace(r, c, shape)) {
                placeBlock(r, c, shape, COLORS[shapeIdx]);
                previewsEl.children[previewIdx].style.visibility = 'hidden';
                checkLines();
                if (Array.from(previewsEl.children).filter(el => el.style.visibility !== 'hidden').length === 0) generatePreviews();
            }
        });

        function canPlace(r, c, shape) {
            for (let i = 0; i < shape.length; i++) {
                for (let j = 0; j < shape[i].length; j++) {
                    if (shape[i][j]) {
                        const nr = r + i, nc = c + j;
                        if (nr < 0 || nr >= BOARD_SIZE || nc < 0 || nc >= BOARD_SIZE || boardState[nr][nc] !== 0) return false;
                    }
                }
            }
            return true;
        }

        function placeBlock(r, c, shape, color) {
            for (let i = 0; i < shape.length; i++) {
                for (let j = 0; j < shape[i].length; j++) {
                    if (shape[i][j]) {
                        boardState[r + i][c + j] = color;
                        const cell = document.getElementById(`cell-${r + i}-${c + j}`);
                        cell.style.backgroundColor = color;
                        cell.classList.add('block-active');
                    }
                }
            }
            score += 10; updateScore();
        }

        function checkLines() {
            let fullRows = [], fullCols = [];
            for (let i = 0; i < BOARD_SIZE; i++) {
                if (boardState[i].every(val => val !== 0)) fullRows.push(i);
                let colFull = true;
                for (let j = 0; j < BOARD_SIZE; j++) if (boardState[j][i] === 0) { colFull = false; break; }
                if (colFull) fullCols.push(i);
            }

            const totalLines = fullRows.length + fullCols.length;
            if (totalLines > 0) {
                // 이펙트 트리거
                showComboEffect(totalLines);
                
                fullRows.forEach(r => boardState[r].fill(0));
                fullCols.forEach(c => { for (let r = 0; r < BOARD_SIZE; r++) boardState[r][c] = 0; });
                score += totalLines * 100 * totalLines; // 콤보 가중치 점수
                updateScore();
                setTimeout(refreshUI, 150);
            }
        }

        function showComboEffect(lines) {
            let msg = "GOOD!";
            if (lines === 2) msg = "GREAT!";
            else if (lines === 3) msg = "EXCELLENT!";
            else if (lines >= 4) msg = "UNBELIEVABLE!";

            comboEl.innerText = msg;
            comboEl.style.display = 'block';
            // 애니메이션 초기화
            comboEl.style.animation = 'none';
            comboEl.offsetHeight; 
            comboEl.style.animation = null;

            setTimeout(() => { comboEl.style.display = 'none'; }, 800);
        }

        function refreshUI() {
            for (let r = 0; r < BOARD_SIZE; r++) {
                for (let c = 0; c < BOARD_SIZE; c++) {
                    const cell = document.getElementById(`cell-${r}-${c}`);
                    const color = boardState[r][c];
                    cell.style.backgroundColor = color || '';
                    if (!color) cell.classList.remove('block-active');
                }
            }
        }

        function updateScore() {
            document.getElementById('score').innerText = score;
            if (score > bestScore) {
                bestScore = score;
                localStorage.setItem('vibeTetrisBestPlus', bestScore);
                document.getElementById('best-score').innerText = bestScore;
            }
        }

        initBoard();
        generatePreviews();
    </script>
</body>
</html>
"""

# Streamlit 인터페이스
components.html(game_html, height=850, scrolling=False)
