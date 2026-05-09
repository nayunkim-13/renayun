import streamlit as st
import streamlit.components.v1 as components

# [1. Streamlit 셋업]
st.set_page_config(
    page_title="바이브 통합 게임 센터",
    page_icon="🕹️",
    layout="centered"
)

# [2. 통합 게임 인터페이스 HTML/JS]
# 이 변수 안에 모든 스타일(Tailwind), 로직(Vanilla JS), 마크업이 포함되어 있습니다.
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Tailwind CSS & 아이콘 CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Noto Sans KR', sans-serif; -webkit-user-select: none; user-select: none; }
        .tab-active { border-bottom: 4px solid #4f46e5; color: #4f46e5; }
        .bingo-cell { transition: all 0.2s; aspect-ratio: 1 / 1; }
        .marked { background-color: #ef4444 !important; color: white; transform: scale(0.9); }
    </style>
</head>
<body class="bg-slate-100 p-2 sm:p-4">

    <div class="max-w-2xl mx-auto bg-white rounded-[2rem] shadow-2xl overflow-hidden border border-gray-100">
        <!-- 상단 탭 메뉴 -->
        <div class="flex bg-gray-50 border-b">
            <button onclick="switchGame('furniture')" id="tab-furniture" class="flex-1 py-4 font-bold text-gray-400 tab-active">
                <i class="fa-solid fa-hammer mr-2"></i> 가구 제작
            </button>
            <button onclick="switchGame('bingo')" id="tab-bingo" class="flex-1 py-4 font-bold text-gray-400">
                <i class="fa-solid fa-border-all mr-2"></i> AI 빙고
            </button>
        </div>

        <!-- [게임 1: 가구 제작 타이쿤 영역] -->
        <div id="furniture-game" class="p-6">
            <div class="flex justify-between bg-amber-50 p-3 rounded-2xl mb-4 border border-amber-100 shadow-sm">
                <div class="text-center"><p class="text-xs text-amber-600">물 💧</p><p id="f-water" class="font-bold">5</p></div>
                <div class="text-center"><p class="text-xs text-amber-600">판자 🪵</p><p id="f-wood" class="font-bold">0</p></div>
                <div class="text-center"><p class="text-xs text-amber-600">가구 ✨</p><p id="f-item" class="font-bold">0</p></div>
            </div>
            
            <div id="f-screen" class="h-64 bg-sky-50 rounded-3xl mb-6 flex flex-col items-center justify-center relative border-2 border-dashed border-sky-200">
                <!-- 농장 뷰 -->
                <div id="view-farm" class="text-center">
                    <div id="f-tree" class="text-7xl mb-4 transition-all duration-500">🌱</div>
                    <div class="w-40 h-3 bg-gray-200 rounded-full mx-auto overflow-hidden">
                        <div id="f-bar" class="h-full bg-green-500 w-0 transition-all"></div>
                    </div>
                    <p class="text-[10px] mt-2 text-gray-400">나무 성장도: <span id="f-percent">0</span>%</p>
                </div>
                <!-- 마이홈 뷰 -->
                <div id="view-home" class="hidden w-full h-full p-4 overflow-y-auto grid grid-cols-5 gap-3 content-start"></div>
            </div>

            <div class="space-y-3">
                <button id="f-main-btn" onclick="handleFurnitureAction()" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-2xl shadow-lg shadow-indigo-100 transition active:scale-95">물 주기 (💧-1)</button>
                <button onclick="toggleFurnitureView()" id="f-view-btn" class="w-full bg-slate-800 text-white py-3 rounded-2xl text-sm font-medium">마이홈 구경하기 🏠</button>
            </div>
        </div>

        <!-- [게임 2: AI 빙고 영역] -->
        <div id="bingo-game" class="hidden p-6">
            <div class="grid grid-cols-4 gap-2 mb-4">
                <div id="b-st-0" class="bg-indigo-600 text-white p-2 rounded-xl text-center text-[10px] shadow-sm">나: 0</div>
                <div id="b-st-1" class="bg-gray-100 text-gray-600 p-2 rounded-xl text-center text-[10px]">AI 1: 0</div>
                <div id="b-st-2" class="bg-gray-100 text-gray-600 p-2 rounded-xl text-center text-[10px]">AI 2: 0</div>
                <div id="b-st-3" class="bg-gray-100 text-gray-600 p-2 rounded-xl text-center text-[10px]">AI 3: 0</div>
            </div>
            
            <div id="b-board" class="grid grid-cols-5 gap-1.5 mb-6"></div>
            
            <div class="bg-slate-50 p-4 rounded-2xl border border-gray-100 text-center">
                <p id="b-msg" class="text-sm font-bold text-slate-700">숫자를 눌러 게임을 시작하세요!</p>
            </div>
        </div>
    </div>

    <script>
        /* --- 공통 로직 --- */
        function switchGame(game) {
            document.getElementById('furniture-game').classList.toggle('hidden', game !== 'furniture');
            document.getElementById('bingo-game').classList.toggle('hidden', game !== 'bingo');
            document.getElementById('tab-furniture').classList.toggle('tab-active', game === 'furniture');
            document.getElementById('tab-bingo').classList.toggle('tab-active', game === 'bingo');
        }

        /* --- 가구 게임 로직 --- */
        let fData = { water: 5, wood: 0, items: 0, growth: 0, mode: 'farm' };
        const treeIcons = ['🌱', '🌿', '🌳', '🌲'];

        function updateFurnitureUI() {
            document.getElementById('f-water').innerText = fData.water;
            document.getElementById('f-wood').innerText = fData.wood;
            document.getElementById('f-item').innerText = fData.items;
            document.getElementById('f-percent').innerText = fData.growth;
            document.getElementById('f-bar').style.width = fData.growth + '%';
            document.getElementById('f-tree').innerText = treeIcons[Math.min(3, Math.floor(fData.growth / 30))];
            
            const mainBtn = document.getElementById('f-main-btn');
            if (fData.growth >= 100) {
                mainBtn.innerText = "나무 베기 (🪵+3)";
                mainBtn.className = "w-full bg-amber-600 hover:bg-amber-700 text-white font-bold py-4 rounded-2xl shadow-lg transition active:scale-95";
            } else {
                mainBtn.innerText = "물 주기 (💧-1)";
                mainBtn.className = "w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-2xl shadow-lg transition active:scale-95";
            }
        }

        function handleFurnitureAction() {
            if (fData.growth < 100 && fData.water > 0) {
                fData.water--; fData.growth += 25;
            } else if (fData.growth >= 100) {
                fData.wood += 3; fData.growth = 0; fData.water += 2;
            }
            updateFurnitureUI();
        }

        function toggleFurnitureView() {
            fData.mode = (fData.mode === 'farm' ? 'home' : 'farm');
            document.getElementById('view-farm').classList.toggle('hidden', fData.mode !== 'farm');
            document.getElementById('view-home').classList.toggle('hidden', fData.mode !== 'home');
            document.getElementById('f-main-btn').classList.toggle('hidden', fData.mode !== 'farm');
            document.getElementById('f-view-btn').innerText = fData.mode === 'farm' ? '마이홈 구경하기 🏠' : '농장으로 돌아가기 🌲';
            
            if (fData.mode === 'home') {
                const home = document.getElementById('view-home');
                home.innerHTML = '';
                if (fData.wood >= 5) { // 가구 자동 제작 시스템
                    const newItems = Math.floor(fData.wood / 5);
                    fData.items += newItems;
                    fData.wood %= 5;
                    updateFurnitureUI();
                }
                for (let i = 0; i < fData.items; i++) home.innerHTML += '<div class="text-3xl text-center">🪑</div>';
            }
        }

        /* --- 빙고 게임 로직 --- */
        let bCalled = [], bGameOver = false;
        let pBoards = [], pMarked = [];

        function initBingo() {
            const gen = () => Array.from({length: 50}, (_, i) => i + 1).sort(() => Math.random() - 0.5).slice(0, 25);
            pBoards = [gen(), gen(), gen(), gen()];
            pMarked = Array.from({length: 4}, () => Array(25).fill(false));
            renderBingo();
        }

        function renderBingo() {
            const boardEl = document.getElementById('b-board');
            boardEl.innerHTML = '';
            pBoards[0].forEach((num, i) => {
                const isMarked = bCalled.includes(num);
                boardEl.innerHTML += `<div onclick="clickBingo(${num})" class="bingo-cell flex items-center justify-center border rounded-xl font-bold text-sm bg-white hover:bg-indigo-50 cursor-pointer ${isMarked ? 'marked' : ''}">${num}</div>`;
            });
        }

        function clickBingo(num) {
            if (bGameOver || bCalled.includes(num)) return;
            processBingoTurn(num);
        }

        function processBingoTurn(num) {
            bCalled.append ? null : bCalled.push(num);
            updateBingoStatus();
            renderBingo();
            if (bGameOver) return;

            // AI 턴 (순차적 실행)
            let turn = 1;
            const aiInterval = setInterval(() => {
                const unmarked = pBoards[turn].filter(n => !bCalled.includes(n));
                const aiPick = unmarked[Math.floor(Math.random() * unmarked.length)];
                bCalled.push(aiPick);
                updateBingoStatus();
                renderBingo();
                if (bGameOver || ++turn > 3) {
                    clearInterval(aiInterval);
                    if (!bGameOver) document.getElementById('b-msg').innerText = "당신의 차례입니다!";
                } else {
                    document.getElementById('b-msg').innerText = `AI ${turn}이(가) 숫자를 부릅니다: ${aiPick}`;
                }
            }, 800);
        }

        function updateBingoStatus() {
            pBoards.forEach((board, pIdx) => {
                let m = board.map(n => bCalled.includes(n));
                let bingo = 0;
                for (let i=0; i<5; i++) {
                    if ([0,1,2,3,4].every(j => m[i*5+j])) bingo++;
                    if ([0,1,2,3,4].every(j => m[j*5+i])) bingo++;
                }
                if ([0,6,12,18,24].every(i => m[i])) bingo++;
                if ([4,8,12,16,20].every(i => m[i])) bingo++;
                
                const el = document.getElementById(`b-st-${pIdx}`);
                el.innerText = `${pIdx === 0 ? '나' : 'AI ' + pIdx}: ${bingo}`;
                if (bingo >= 3) {
                    bGameOver = true;
                    document.getElementById('b-msg').innerText = `🎊 게임 종료! 승자: ${pIdx === 0 ? '나' : 'AI ' + pIdx}`;
                }
            });
        }

        initBingo();
        updateFurnitureUI();
    </script>
</body>
</html>
"""

# [3. Streamlit 컴포넌트 렌더링]
st.title("Vibe All-in-One Center")
st.caption("가구 제작 타이쿤 & 4인 AI 빙고 대결")

# HTML 컴포넌트를 호출 (스크롤 방지를 위해 높이를 넉넉히 설정)
components.html(game_html, height=750, scrolling=False)

st.markdown("""
---
### 🛠️ 실행 및 배포 가이드
1. **로컬 실행**: `pip install streamlit` 후 `streamlit run app.py`
2. **GitHub 배포**: 이 파일을 `app.py`라는 이름으로 저장하여 저장소에 Push 하세요.
3. **Streamlit Cloud**: GitHub 연동 후 배포하면 웹에서 즉시 플레이 가능합니다.
""")
