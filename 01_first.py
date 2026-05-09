import pygame
import sys
import random

# 1. 기본 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("바이브 코딩 - 귀여운 가구 만들기")
clock = pygame.time.Clock()

# 색상 팔레트 (귀여운 파스텔 톤)
WHITE = (255, 255, 255)
GRASS = (184, 223, 130)
BROWN = (139, 69, 19)
LEAF = (34, 139, 34)
GOLD = (255, 215, 0)
SKY = (135, 206, 235)
WOOD_PANEL = (222, 184, 135)

# 폰트 설정
try:
    font = pygame.font.SysFont("malgungothic", 20)
    title_font = pygame.font.SysFont("malgungothic", 35, bold=True)
except:
    font = pygame.font.Font(None, 30)
    title_font = pygame.font.Font(None, 50)

# 2. 게임 변수
water = 5
wood = 0
furniture_count = 0
tree_growth = 0  # 0 to 100
current_view = "farm"  # farm, craft, home

# 버튼 영역 설정
farm_btn = pygame.Rect(50, 530, 100, 40)
craft_btn = pygame.Rect(170, 530, 100, 40)
home_btn = pygame.Rect(290, 530, 100, 40)
action_btn = pygame.Rect(550, 400, 200, 60)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, (0,0,0), rect, 2, border_radius=10)
    text_img = font.render(text, True, (0,0,0))
    text_rect = text_img.get_rect(center=rect.center)
    screen.blit(text_img, text_rect)

# 3. 메인 게임 루프
running = True
while running:
    screen.fill(SKY)
    
    # 상단 상태바
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 50))
    draw_text(f"💧 물: {water}  |  🪵 나무판자: {wood}  |  🪑 가구: {furniture_count}", font, (50, 50, 50), 20, 15)

    # 마우스 위치 확인
    mouse_pos = pygame.mouse.get_pos()

    # --- 화면별 렌더링 ---
    if current_view == "farm":
        # 농장 배경
        pygame.draw.rect(screen, GRASS, (0, 300, WIDTH, 300))
        # 나무 그리기
        trunk_height = int(tree_growth * 1.5)
        if tree_growth > 0:
            pygame.draw.rect(screen, BROWN, (380, 450 - trunk_height, 40, trunk_height))
        if tree_growth >= 100:
            pygame.draw.circle(screen, LEAF, (400, 450 - trunk_height), 60)
            draw_button(action_btn, "나무 베기 (🪵+3)", (200, 200, 200))
        else:
            draw_button(action_btn, "물 주기 (💧-1)", (173, 216, 230))
        draw_text(f"나무 성장도: {tree_growth}%", title_font, (0,0,0), 300, 100)

    elif current_view == "craft":
        screen.fill(WOOD_PANEL)
        draw_text("🔨 가공 작업대", title_font, (0,0,0), 300, 100)
        draw_text("나무판자 5개로 멋진 가구를 만듭니다.", font, (50,50,50), 280, 160)
        
        # 작업대 이미지 대용 (박스)
        pygame.draw.rect(screen, (101, 67, 33), (250, 220, 300, 150), border_radius=15)
        draw_button(action_btn, "가구 제작 (🪑+1)", (255, 165, 0))

    elif current_view == "home":
        screen.fill((255, 250, 240)) # 상아색 벽지
        pygame.draw.rect(screen, (139, 69, 19), (0, 450, WIDTH, 150)) # 바닥
        draw_text("🏠 우리 집 꾸미기", title_font, (0,0,0), 280, 80)
        
        # 가구 수만큼 가구 그리기
        for i in range(furniture_count):
            x_pos = 100 + (i * 120)
            if x_pos < 700:
                pygame.draw.rect(screen, (205, 133, 63), (x_pos, 400, 80, 50)) # 의자/탁자 베이스
                pygame.draw.rect(screen, (139, 69, 19), (x_pos+10, 360, 60, 40)) # 등받이

    # --- 하단 메뉴 버튼 ---
    draw_button(farm_btn, "농장", (184, 223, 130) if current_view == "farm" else WHITE)
    draw_button(craft_btn, "공방", (222, 184, 135) if current_view == "craft" else WHITE)
    draw_button(home_btn, "마이홈", (255, 250, 240) if current_view == "home" else WHITE)

    # 4. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 메뉴 이동
            if farm_btn.collidepoint(mouse_pos): current_view = "farm"
            if craft_btn.collidepoint(mouse_pos): current_view = "craft"
            if home_btn.collidepoint(mouse_pos): current_view = "home"

            # 액션 버튼 클릭
            if action_btn.collidepoint(mouse_pos):
                if current_view == "farm":
                    if tree_growth < 100 and water > 0:
                        water -= 1
                        tree_growth += 25
                    elif tree_growth >= 100:
                        wood += 3
                        tree_growth = 0
                        water += 2 # 나무 베면 물을 조금 얻음
                
                elif current_view == "craft":
                    if wood >= 5:
                        wood -= 5
                        furniture_count += 1
                        print("가구 완성!")

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
