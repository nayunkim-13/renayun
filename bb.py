import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 설정
st.set_page_config(page_title="Vibe Block Tetris Pro", layout="centered")

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
        /* 보드 및 셀 설정 */
        .grid-cell { width: 45px; height: 45px; border: 1px solid rgba(0,0,0,0.03); transition: all 0.2s; }
        .block-active { border-radius: 8px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); }
        
        /* 드래그 아이템 설정: 크기 100% 유지 */
        .preview-item { cursor: grab; transition: transform 0.1s; }
        .preview-item:active { cursor: grabbing; }
        
        .score-font { font-family: 'Orbitron', sans-serif; }
        .board-container { box-shadow: 0 20px 50px rgba(0,0,0,0.08); background: white; padding: 12px; border-radius: 24px; }
        
        /* 드래그 중인 이미지 투명도 조절 */
        .dragging { opacity: 0.4; }
    </style>
</head>
<body>

    <!-- 헤더: 점수 표시 -->
    <div class="mb-6 text-center">
        <h1 class="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent score-font uppercase tracking-tighter">Block Tetris Pro</h1>
        <div class="flex gap-10 justify-center items-center mt-4">
            <div class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Score <p id="score" class="text-3xl text-slate-800 score-font">0</p></div>
            <div class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Best <p id="best-score" class="text-3xl text-blue-500 score-font">0</p></div>
        </div>
    </div>

    <!-- 메인 게임 보드 -->
    <div id="board" class="board-container mb-10">
        <div id="grid-container" class="grid grid-cols-8 gap-1">
            <!-- 셀은 JS에서 생성 -->
        </div>
    </div>

    <!-- 하단 프리뷰 영역 -->
    <div id="previews" class="flex justify-around items-center w-full max-w-md bg-white/70 backdrop-blur-md p-6 rounded-[2.5rem] border border-white shadow-xl min-h-[160px]">
        <!-- 프리뷰 블록은 JS에서 생성 -->
    </div>

    <script>
        const BOARD_SIZE = 8;
        const CELL_SIZE = 45; 
        const GAP = 4; // grid gap (1 = 4px in tailwind)
        
        let score = 0;
        let bestScore = localStorage.getItem('blockTetrisBestPro') || 0;
        let boardState = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
        
        const SHAPES = [
            [[1,1,1,1]], [[1,1],[1,1]], [[1,1,1],[0,1,0]], 
            [[1,0],[1,0],[1,1]], [[1,1,1]], [[1]], [[1,1]]
        ];
        const COLORS = ['#38bdf8', '#3b82f6', '#6366f1', '#8b5cf6', '#d946ef', '#f43f5e', '#f59e0b'];

        const gridContainer = document.getElementById('grid-container');
        const previewsEl = document.getElementById('previews');

        // 1. 초기 보드 생성
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

        // 2. 프리뷰 블록 생성 (정확한 드래그 핸들링 포함)
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

                shape.forEach((row, rIdx) => {
                    row.forEach((cellVal, cIdx) => {
                        const div = document.createElement('div');
                        div.style.width = `${CELL_SIZE}px`;
                        div.style.height = `${CELL_SIZE}px`;
                        if(cellVal) {
                            div.style.backgroundColor = color;
                            div.className = 'rounded-md shadow-sm';
                        }
                        grid.appendChild(div);
                    });
                });

                container.appendChild(grid);
                previewsEl.appendChild(container);

                // 드래그 시작 시 데이터 전송
                container.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('shapeIdx', shapeIdx);
                    e.dataTransfer.setData('previewIdx', i);
                    // 마우스가 클릭한 좌표(오프셋)를 전달하여 정확한 배치를 도움
                    e.dataTransfer.setData('offsetX', e.offsetX);
                    e.dataTransfer.setData('offsetY', e.offsetY);
                    
                    setTimeout(() => container.classList.add('dragging'), 0);
                });
                
                container.addEventListener('dragend', () => container.classList.remove('dragging'));
            }
        }

        // 3. 드롭 및 좌표 계산 로직 (핵심 수정)
        gridContainer.addEventListener('dragover', (e) => {
            e.preventDefault(); // 드롭 허용
        });

        gridContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            const shapeIdx = e.dataTransfer.getData('shapeIdx');
            const previewIdx = e.dataTransfer.getData('previewIdx');
            const offX = parseInt(e.dataTransfer.getData('offsetX'));
            const offY = parseInt(e.dataTransfer.getData('offsetY'));
            
            const shape = SHAPES[shapeIdx];
            const rect = gridContainer.getBoundingClientRect();
            
            // 실제 드롭된 위치에서 클릭 오프셋을 빼서 블록의 왼쪽 상단 기준점 계산
            const mouseX = e.clientX - rect.left - offX;
            const mouseY = e.clientY - rect.top - offY;
            
            // 셀 크기(45) + 간격(4) = 약 49px 단위로 인덱스 계산
            const c = Math.round(mouseX / (CELL_SIZE + 4));
            const r = Math.round(mouseY / (CELL_SIZE + 4));

            if (canPlace(r, c, shape)) {
                placeBlock(r, c, shape, COLORS[shapeIdx]);
                previewsEl.children[previewIdx].style.visibility = 'hidden';
                checkLines();
                
                // 프리뷰 리필 체크
                const remaining = Array.from(previewsEl.children).filter(el => el.style.visibility !== 'hidden');
                if (remaining.length === 0) generatePreviews();
            }
        });

        // 배치 가능 여부 확인 (범위 체크 강화)
        function canPlace(r, c, shape) {
            for (let i = 0; i < shape.length; i++) {
                for (let j = 0; j < shape[i].length; j++) {
                    if (shape[i][j]) {
                        const nr = r + i;
                        const nc = c + j;
                        // 보드 범위를 벗어나거나 이미 블록이 있는 경우
                        if (nr < 0 || nr >= BOARD_SIZE || nc < 0 || nc >= BOARD_SIZE || boardState[nr][nc] !== 0) {
                            return false;
                        }
                    }
                }
            }
            return true;
        }

        // 블록 배치
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
            score += 10;
            updateScore();
        }

        // 완성된 라인 체크
        function checkLines() {
            let fullRows = [];
            let fullCols = [];

            for (let i = 0; i < BOARD_SIZE; i++) {
                if (boardState[i].every(val => val !== 0)) fullRows.push(i);
                let colFull = true;
                for (let j = 0; j < BOARD_SIZE; j++) {
                    if (boardState[j][i] === 0) { colFull = false; break; }
                }
                if (colFull) fullCols.push(i);
            }

            fullRows.forEach(r => boardState[r].fill(0));
            fullCols.forEach(c => {
                for (let r = 0; r < BOARD_SIZE; r++) boardState[r][c] = 0;
            });

            if (fullRows.length > 0 || fullCols.length > 0) {
                score += (fullRows.length + fullCols.length) * 100;
                updateScore();
                // 시각적 업데이트를 위해 약간의 지연 후 렌더링
                setTimeout(refreshUI, 100);
            }
        }

        // 보드 UI 갱신
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
                localStorage.setItem('blockTetrisBestPro', bestScore);
                document.getElementById('best-score').innerText = bestScore;
            }
        }

        // 실행
        initBoard();
        generatePreviews();
    </script>
</body>
</html>
"""

# Streamlit 호출
components.html(game_html, height=850, scrolling=False)

st.markdown("""
### 🚀 블록 테트리스 프로 가이드
- **정밀한 드롭**: 블록의 어떤 지점을 잡아도 잡은 위치 그대로 보드에 안착합니다.
- **최고 기록**: 브라우저를 닫아도 스코어가 유지됩니다.
- **팁**: 가로/세로를 동시에 터뜨려 콤보 점수를 노려보세요!
""")
