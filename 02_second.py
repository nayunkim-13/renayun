import random
import os
import time

# [1. 게임 설정 및 상수]
SIZE = 5  # 5x5 빙고
MAX_NUM = 50  # 1부터 50까지의 숫자 사용

class BingoPlayer:
    def __init__(self, name, is_ai=True):
        self.name = name
        self.is_ai = is_ai
        self.board = self.generate_board()
        self.marked = [[False for _ in range(SIZE)] for _ in range(SIZE)]
        self.bingo_count = 0

    def generate_board(self):
        nums = random.sample(range(1, MAX_NUM + 1), SIZE * SIZE)
        return [nums[i:i + SIZE] for i in range(0, len(nums), SIZE)]

    def mark_number(self, num):
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == num:
                    self.marked[r][c] = True
                    return True
        return False

    def check_bingo(self):
        count = 0
        # 가로 체크
        for row in self.marked:
            if all(row): count += 1
        # 세로 체크
        for c in range(SIZE):
            if all(self.marked[r][c] for r in range(SIZE)): count += 1
        # 대각선 체크
        if all(self.marked[i][i] for i in range(SIZE)): count += 1
        if all(self.marked[i][SIZE - 1 - i] for i in range(SIZE)): count += 1
        
        self.bingo_count = count
        return count

# [2. 유틸리티 함수]
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_game_status(players, called_nums):
    clear_screen()
    print("=" * 60)
    print(f" 🏁  4인 숫자 빙고 게임 (현재 호출된 숫자: {len(called_nums)}개)")
    print("=" * 60)
    
    # 내 보드 출력
    user = players[0]
    print(f"\n[{user.name}님의 보드] - 현재 {user.bingo_count} 빙고")
    for r in range(SIZE):
        row_str = ""
        for c in range(SIZE):
            val = f"{user.board[r][c]:2}"
            if user.marked[r][c]:
                row_str += f" \033[91m[{val}]\033[0m " # 마킹된 숫자는 빨간색
            else:
                row_str += f"  {val}  "
        print(row_str)
    
    print("\n" + "-" * 60)
    # AI 상태 요약
    ai_status = " | ".join([f"{p.name}: {p.bingo_count}빙고" for p in players[1:]])
    print(f"🤖 AI 현황: {ai_status}")
    print("-" * 60)

# [3. 메인 게임 루프]
def start_bingo():
    # 플레이어 생성 (진행자 역할은 시스템이 수행)
    players = [
        BingoPlayer("User", is_ai=False),
        BingoPlayer("AI_Alpha"),
        BingoPlayer("AI_Beta"),
        BingoPlayer("AI_Gamma")
    ]
    
    called_numbers = []
    turn = 0
    
    while True:
        current_player = players[turn % 4]
        print_game_status(players, called_numbers)
        
        # 숫자 선택
        if not current_player.is_ai:
            while True:
                try:
                    choice = int(input(f"\n👉 숫자를 부르세요 (1-{MAX_NUM}): "))
                    if 1 <= choice <= MAX_NUM and choice not in called_numbers:
                        break
                    print("❌ 이미 불렀거나 범위를 벗어난 숫자입니다.")
                except ValueError:
                    print("❌ 숫자만 입력해주세요.")
        else:
            print(f"\n💬 {current_player.name}이(가) 고민 중...")
            time.sleep(1.5)
            # AI의 전략: 자신의 보드 중 아직 마킹 안 된 숫자 중 랜덤 선택
            unmarked = []
            for r in range(SIZE):
                for c in range(SIZE):
                    if not current_player.marked[r][c]:
                        unmarked.append(current_player.board[r][c])
            choice = random.choice(unmarked)
            print(f"📢 {current_player.name}: \"{choice}!\"")
            time.sleep(1)

        # 모든 플레이어 마킹 및 빙고 체크
        called_numbers.append(choice)
        winners = []
        for p in players:
            p.mark_number(choice)
            if p.check_bingo() >= 3: # 3빙고 달성 시 승리
                winners.append(p.name)
        
        # 승자 확인
        if winners:
            print_game_status(players, called_numbers)
            print("\n" + "🎉" * 20)
            print(f"게임 종료! 승리자: {', '.join(winners)}")
            print("🎉" * 20)
            break
            
        turn += 1

if __name__ == "__main__":
    start_bingo()
