import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 설정
st.set_page_config(page_title="Vibe Block Blast", layout="centered")

# 전체 게임 로직 (HTML + CSS + JS)
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Noto+Sans+KR:wght@400;700&display=swap');
        body { font-family: 'Noto Sans KR', sans-serif; background: #0f172a; color: white; overflow: hidden; }
        .grid-cell { width: 40px; height: 40px; border: 1px solid rgba(255,255,255,0.05); transition: all 0.1s; }
        .block-active { border-radius: 8px; box-shadow: inset 0 0 10px rgba(0,0,0,0.2); }
        .preview-container { min-height: 120px; }
        .dragging { opacity: 0.5; transform: scale(1.1); }
        .score-font { font-family: 'Orbitron', sans-serif; }
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-screen p-4">

    <!-- 게임 헤더 -->
    <div class="mb-6 text-center">
        <h1 class="text-4xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent score-font">BLOCK BLAST</h1>
        <div class="flex gap-8 justify-center items-center">
            <div class="text-gray-400 text-sm">SCORE <p id="score" class="text-2xl text-white score-font">0</p></div>
            <div class="text-gray-400 text-sm">BEST <p id="best-score" class="text-2xl text-yellow-400 score-font">0</p></div>
        </div>
    </div>

    <!-- 메인 게임 보드 (8x8) -->
    <div id="board" class="grid grid-cols-8 gap-1 bg-slate-800 p-2 rounded-xl shadow-2xl border-4 border-slate-700 mb-8">
        <!-- JS에서 셀 생성 -->
    </div>

    <!-- 하단 블록 프리뷰 영역 (3개 선택지) -->
    <div id="previews" class="flex justify-around w-full max-w-md bg-slate-900/50 p-4 rounded-2xl border border-white/10 preview-container">
        <!-- JS에서 프리뷰 블록 생성 -->
    </div>

    <script>
        const BOARD_SIZE = 8;
        let score = 0;
        let bestScore = localStorage.getItem('blockBlastBest') || 0;
        let boardState = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
        
        // 블록 모양 정의
        const SHAPES = [
            [[1,1,1,1]], // 1x4
            [[1,1],[1,1]], // 2x2
            [[1,1,1],[0,1,0]], // T
            [[1,0],[1,0],[1,1]], // L
            [[1,1,1]], // 1x3
            [[1]], // 1x1
            [[1,1]] // 1x2
        ];
        const COLORS = ['#22d3ee', '#3b82f6', '#818cf8', '#a855f7', '#ec4899', '#f43f5e', '#fbbf24'];

        let currentPreviews = [];

        // 보드 초기화
        const boardEl = document.getElementById('board');
        function initBoard() {
            boardEl.innerHTML = '';
            for (let r = 0; r < BOARD_SIZE; r++) {
                for (let c = 0; c < BOARD_SIZE; c++) {
                    const cell = document.createElement('div');
                    cell.className = 'grid-cell bg-slate-700/30 rounded-md';
                    cell.dataset.r = r;
                    cell.dataset.c = c;
                    // 드롭 이벤트 리스너
                    cell.onscreen = () => {}; 
                    boardEl.appendChild(cell);
                }
            }
            document.getElementById('best-score').innerText = bestScore;
        }

        // 새로운 프리뷰 블록 생성
        function generatePreviews() {
            const previewsEl = document.getElementById('previews');
            previewsEl.innerHTML = '';
            currentPreviews = [];

            for (let i = 0; i < 3; i++) {
                const shapeIdx = Math.floor(Math.random() * SHAPES.length);
                const color = COLORS[shapeIdx];
                const shape = SHAPES[shapeIdx];
                
                const container = document.createElement('div');
                container.className = 'cursor-grab active:cursor-grabbing p-2 hover:bg-white/5 rounded-lg transition';
                container.draggable = true;
                
                // 미니 그리드로 블록 그리기
                const grid = document.createElement('div');
                grid.style.display = 'grid';
                grid.style.gridTemplateColumns = `repeat(${shape[0].length}, 20px)`;
                grid.style.gap = '2px';

                shape.forEach(row => {
                    row.forEach(cell => {
                        const div = document.createElement('div');
                        div.style.width = '20px';
                        div.style.height = '20px';
                        if(cell) {
                            div.style.backgroundColor = color;
                            div.className = 'rounded-sm';
                        }
                        grid.appendChild(div);
                    });
                });

                container.appendChild(grid);
                previewsEl.appendChild(container);

                // 드래그 로직 (모바일/데스크탑 통합을 위해 데이터 저장)
                container.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('shapeIdx', shapeIdx);
                    e.dataTransfer.setData('previewIdx', i);
                    container.classList.add('dragging');
                });
                container.addEventListener('dragend', () => container.classList.remove('dragging'));
                
                currentPreviews.push({ shape, color, used: false });
            }
        }

        // 드롭 처리
        boardEl.addEventListener('dragover', (e) => e.preventDefault());
        boardEl.addEventListener('drop', (e) => {
            e.preventDefault();
            const shapeIdx = e.dataTransfer.getData('shapeIdx');
            const previewIdx = e.dataTransfer.getData('previewIdx');
            const rect = boardEl.getBoundingClientRect();
            
            // 마우스 위치 기준으로 보드 좌표 계산
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const c = Math.floor(x / 44);
            const r = Math.floor(y / 44);

            if (canPlace(r, c, SHAPES[shapeIdx])) {
                placeBlock(r, c, SHAPES[shapeIdx], COLORS[shapeIdx]);
                // 사용한 프리뷰 제거
                document.getElementById('previews').children[previewIdx].style.visibility = 'hidden';
                checkLines();
                
                // 3개 다 썼으면 새로 생성
                if (++usedCount === 3) {
                    usedCount = 0;
                    generatePreviews();
                }
            }
        });

        let usedCount = 0;

        function canPlace(r, c, shape) {
            for (let i = 0; i < shape.length; i++) {
                for (let j = 0; j < shape[i].length; j++) {
                    if (shape[i][j]) {
                        const nr = r + i, nc = c + j;
                        if (nr >= BOARD_SIZE || nc >= BOARD_SIZE || boardState[nr][nc]) return false;
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
            let rowsToClear = [];
            let colsToClear = [];

            // 가로 체크
            for (let r = 0; r < BOARD_SIZE; r++) {
                if (boardState[r].every(cell => cell !== 0)) rowsToClear.push(r);
            }
            // 세로 체크
            for (let c = 0; c < BOARD_SIZE; c++) {
                let full = true;
                for (let r = 0; r < BOARD_SIZE; r++) {
                    if (boardState[r][c] === 0) { full = false; break; }
                }
                if (full) colsToClear.push(c);
            }

            // 지우기 및 점수
            rowsToClear.forEach(r => {
                for (let c = 0; c < BOARD_SIZE; c++) boardState[r][c] = 0;
            });
            colsToClear.forEach(c => {
                for (let r = 0; r < BOARD_SIZE; r++) boardState[r][c] = 0;
            });

            if (rowsToClear.length > 0 || colsToClear.length > 0) {
                score += (rowsToClear.length + colsToClear.length) * 100;
                updateScore();
                // 보드 다시 그리기 (애니메이션 효과 가능)
                redrawBoard();
            }
        }

        function redrawBoard() {
            for (let r = 0; r < BOARD_SIZE; r++) {
                for (let c = 0; c < BOARD_SIZE; c++) {
                    const cell = boardEl.children[r * BOARD_SIZE + c];
                    cell.style.backgroundColor = boardState[r][c] || 'transparent';
                    if(!boardState[r][c]) cell.classList.remove('block-active');
                }
            }
        }

        function updateScore() {
            document.getElementById('score').innerText = score;
            if (score > bestScore) {
                bestScore = score;
                localStorage.setItem('blockBlastBest', bestScore);
                document.getElementById('best-score').innerText = bestScore;
            }
        }

        initBoard();
        generatePreviews();
    </script>
</body>
</html>
"""

# Streamlit에 컴포넌트 주입
components.html(game_html, height=800)

st.markdown("""
---
### 🕹️ 게임 방법
1. 하단의 **블록 프리뷰**를 드래그해서 상단 **8x8 보드**에 놓으세요.
2. 가로 또는 세로 한 줄을 꽉 채우면 줄이 터지면서 점수를 얻습니다.
3. 더 이상 블록을 놓을 공간이 없으면 게임 오버! (새로고침으로 재시작)
""")
