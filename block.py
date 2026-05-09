import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 설정
st.set_page_config(page_title="Vibe Block Tetris", layout="centered")

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
            touch-action: none;
        }
        /* 셀 크기 고정 */
        .grid-cell { width: 44px; height: 44px; border: 1px solid rgba(0,0,0,0.03); transition: background-color 0.2s; }
        .block-active { border-radius: 8px; box-shadow: inset 0 0 12px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); }
        
        /* 드래그 시 크기 유지 설정 */
        .preview-item { transition: transform 0.2s; cursor: grab; }
        .preview-item:active { cursor: grabbing; }
        .dragging { opacity: 0.7; transform: scale(1) !important; } /* 작아지지 않게 고정 */
        
        .score-font { font-family: 'Orbitron', sans-serif; }
        .board-container { box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); }
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-screen p-4">

    <!-- 헤더 영역 -->
    <div class="mb-6 text-center">
        <h1 class="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent score-font">BLOCK TETRIS</h1>
        <div class="flex gap-12 justify-center items-center mt-4">
            <div class="text-slate-400 text-xs font-bold uppercase tracking-tighter">Current Score <p id="score" class="text-3xl text-slate-800 score-font">0</p></div>
            <div class="text-slate-400 text-xs font-bold uppercase tracking-tighter">Best Record <p id="best-score" class="text-3xl text-blue-500 score-font">0</p></div>
        </div>
    </div>

    <!-- 메인 8x8 보드 -->
    <div id="board" class="grid grid-cols-8 gap-1 bg-white p-3 rounded-2xl board-container border border-white mb-10">
        <!-- JS가 셀을 채웁니다 -->
    </div>

    <!-- 하단 블록 선택지 -->
    <div id="previews" class="flex justify-around items-center w-full max-w-md bg-white/60 backdrop-blur-md p-6 rounded-[2.5rem] border border-white shadow-xl min-h-[160px]">
        <!-- JS가 블록을 채웁니다 -->
    </div>

    <script>
        const BOARD_SIZE = 8;
        const CELL_SIZE = 44;
        const GAP = 4; // grid gap
        let score = 0;
        let bestScore = localStorage.getItem('vibeTetrisBest') || 0;
        let boardState = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
        
        const SHAPES = [
            [[1,1,1,1]], [[1,1],[1,1]], [[1,1,1],[0,1,0]], 
            [[1,0],[1,0],[1,1]], [[1,1,1]], [[1]], [[1,1]]
        ];
        const COLORS = ['#38bdf8', '#3b82f6', '#6366f1', '#8b5cf6', '#d946ef', '#f43f5e', '#f59e0b'];

        const boardEl = document.getElementById('board');
        const previewsEl = document.getElementById('previews');

        // [1] 보드 초기화
        function initBoard() {
            boardEl.innerHTML = '';
            for (let r = 0; r < BOARD_SIZE; r++) {
                for (let c = 0; c < BOARD_SIZE; c++) {
                    const cell = document.createElement('div');
                    cell.className = 'grid-cell bg-slate-50 rounded-lg';
                    boardEl.appendChild(cell);
                }
            }
            document.getElementById('best-score').innerText = bestScore;
        }

        // [2] 프리뷰 블록 생성 (크기 유지 로직 적용)
        function generatePreviews() {
            previewsEl.innerHTML = '';
            for (let i = 0; i < 3; i++) {
                const shapeIdx = Math.floor(Math.random() * SHAPES.length);
                const color = COLORS[shapeIdx];
                const shape = SHAPES[shapeIdx];
                
                const container = document.createElement('div');
                container.className = 'preview-item p-2';
                container.draggable = true;
                
                const grid = document.createElement('div');
                grid.style.display = 'grid';
                grid.style.gridTemplateColumns = `repeat(${shape[0].length}, ${CELL_SIZE}px)`;
                grid.style.gap = '1px';

                shape.forEach(row => {
                    row.forEach(cell => {
                        const div = document.createElement('div');
                        div.style.width = `${CELL_SIZE}px`;
                        div.style.height = `${CELL_SIZE}px`;
                        if(cell) {
                            div.style.backgroundColor = color;
                            div.className = 'rounded-md shadow-sm';
                        }
                        grid.appendChild(div);
                    });
                });

                container.appendChild(grid);
                previewsEl.appendChild(container);

                // 드래그 시작 시 데이터 저장 및 스타일 적용
                container.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('shapeIdx', shapeIdx);
                    e.dataTransfer.setData('previewIdx', i);
                    // 드래그 이미지 크기 조절 방지 (기본 동작 유지)
                    setTimeout(() => container.classList.add('dragging'), 0);
                });
                
                container.addEventListener('dragend', () => {
                    container.classList.remove('dragging');
                });
            }
        }

        // [3] 드롭 처리 및 선 제거 로직
        boardEl.addEventListener('dragover', (e) => e.preventDefault());
        boardEl.addEventListener('drop', (e) => {
            e.preventDefault();
            const shapeIdx = e.dataTransfer.getData('shapeIdx');
            const previewIdx = e.dataTransfer.getData('previewIdx');
            const shape = SHAPES[shapeIdx];
            const rect = boardEl.getBoundingClientRect();
            
            // 드래그한 좌표를 보드 인덱스로 변환
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const c = Math.floor(x / (CELL_SIZE + GAP));
            const r = Math.floor(y / (CELL_SIZE + GAP));

            if (canPlace(r, c, shape)) {
                placeBlock(r, c, shape, COLORS[shapeIdx]);
                previewsEl.children[previewIdx].style.visibility = 'hidden';
                checkLines();
                
                // 모든 프리뷰 소진 시 새로 생성
                const remaining = Array.from(previewsEl.children).filter(el => el.style.visibility !== 'hidden');
                if (remaining.length === 0) generatePreviews();
            }
        });

        function canPlace(r, c, shape) {
            for (let i = 0; i < shape.length; i++) {
                for (let j = 0; j < shape[i].length; j++) {
                    if (shape[i][j]) {
                        const nr = r + i, nc = c + j;
                        if (nr < 0 || nr >= BOARD_SIZE || nc < 0 || nc >= BOARD_SIZE || boardState[nr][nc]) return false;
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
                        const cell = boardEl.children[(r + i) * BOARD_SIZE + (c + j)];
                        cell.style.backgroundColor = color;
                        cell.classList.add('block-active');
                    }
                }
            }
            score += 10;
            updateScore();
        }

        function checkLines() {
            let rows = [], cols = [];
            for (let i = 0; i < BOARD_SIZE; i++) {
                if (boardState[i].every(v => v !== 0)) rows.push(i);
                if (boardState.every(row => row[i] !== 0)) cols.push(i);
            }

            rows.forEach(r => boardState[r].fill(0));
            cols.forEach(c => boardState.forEach(row => row[c] = 0));

            if (rows.length > 0 || cols.length > 0) {
                score += (rows.length + cols.length) * 100;
                updateScore();
                setTimeout(renderBoard, 150);
            }
        }

        function renderBoard() {
            for (let r = 0; r < BOARD_SIZE; r++) {
                for (let c = 0; c < BOARD_SIZE; c++) {
                    const cell = boardEl.children[r * BOARD_SIZE + c];
                    cell.style.backgroundColor = boardState[r][c] || '';
                    if(!boardState[r][c]) cell.classList.remove('block-active');
                }
            }
        }

        function updateScore() {
            document.getElementById('score').innerText = score;
            if (score > bestScore) {
                bestScore = score;
                localStorage.setItem('vibeTetrisBest', bestScore);
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
components.html(game_html, height=850)
