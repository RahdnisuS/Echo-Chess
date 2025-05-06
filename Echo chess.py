import pygame
import math
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CENTER = (300, 300)
RADIUS = 180
NODE_RADIUS = 25
FPS = 60

# Colors
BG_COLOR = (30, 30, 30)
CIRCLE_COLOR = (200, 200, 200)
HOVER_COLOR = (255, 255, 0)
PLAYER_COLOR = (0, 200, 255)
AI_COLOR = (255, 100, 100)
LINE_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 255)

# Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circular Tic Tac Toe")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
large_font = pygame.font.SysFont(None, 48)

# Positions and logic
CIRCLE_POSITIONS = [
    (CENTER[0] + RADIUS * math.cos(math.radians(45 * i)),
     CENTER[1] + RADIUS * math.sin(math.radians(45 * i))) for i in range(8)
]
CIRCLE_POSITIONS.append(CENTER)  # center spot (index 8)

ADJACENT = {
    0: [1, 7, 8], 1: [0, 2, 8], 2: [1, 3, 8], 3: [2, 4, 8],
    4: [3, 5, 8], 5: [4, 6, 8], 6: [5, 7, 8], 7: [6, 0, 8],
    8: list(range(8))
}

WINNING_LINES = [
    [0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 0],
    [1, 8, 5], [3, 8, 7], [0, 8, 4], [2, 8, 6]
]

# Game states
def reset_game():
    global player_pieces, ai_pieces, occupied, selected, game_over, winner, turn, animations
    player_pieces = [0, 1, 2]
    ai_pieces = [5, 6, 7]
    occupied = [' '] * 9
    for p in player_pieces:
        occupied[p] = 'X'
    for a in ai_pieces:
        occupied[a] = 'O'
    selected = None
    game_over = False
    winner = None
    turn = 'Player'
    animations = []

reset_game()
game_started = False

# Helper functions
def draw_text(text, x, y, font, color=TEXT_COLOR):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def animate_moves():
    for anim in animations[:]:
        piece, start, end, symbol, timer = anim
        t = min(1.0, timer / 10)
        x = (1 - t) * CIRCLE_POSITIONS[start][0] + t * CIRCLE_POSITIONS[end][0]
        y = (1 - t) * CIRCLE_POSITIONS[start][1] + t * CIRCLE_POSITIONS[end][1]
        color = PLAYER_COLOR if symbol == 'X' else AI_COLOR
        pygame.draw.circle(screen, color, (int(x), int(y)), NODE_RADIUS - 5)
        anim[4] += 1
        if t >= 1.0:
            animations.remove(anim)

def draw_board(hover=None):
    screen.fill(BG_COLOR)
    
    # Instructions panel
    pygame.draw.rect(screen, (50, 50, 70), (600, 0, 200, HEIGHT))
    draw_text("Instructions:", 610, 20, font)
    draw_text("- Get 3 in a row", 610, 60, font)
    draw_text("- Click to move", 610, 90, font)
    draw_text("- One step at a time", 610, 120, font)
    draw_text("- Beat the AI!", 610, 150, font)

    # Draw lines
    for line in WINNING_LINES:
        pygame.draw.line(screen, LINE_COLOR, CIRCLE_POSITIONS[line[0]], CIRCLE_POSITIONS[line[2]], 2)

    # Draw circles
    for i, pos in enumerate(CIRCLE_POSITIONS):
        color = CIRCLE_COLOR
        if i == selected:
            color = HOVER_COLOR
        elif hover is not None and i == hover:
            if (selected is not None and i in ADJACENT[selected]) or (selected is None and i in player_pieces):
                color = HOVER_COLOR
        pygame.draw.circle(screen, color, pos, NODE_RADIUS, 3)

    # Draw reset button
    pygame.draw.rect(screen, BUTTON_COLOR, (WIDTH - 140, HEIGHT - 50, 120, 35))
    draw_text("Reset", WIDTH - 110, HEIGHT - 47, font)

    # Draw pieces
    for i, occ in enumerate(occupied):
        if occ == 'X' and (selected != i):
            pygame.draw.circle(screen, PLAYER_COLOR, CIRCLE_POSITIONS[i], NODE_RADIUS - 5)
        elif occ == 'O':
            pygame.draw.circle(screen, AI_COLOR, CIRCLE_POSITIONS[i], NODE_RADIUS - 5)

    animate_moves()

    # Result
    if game_over:
        draw_text(f"{winner} Wins!", 250, 20, large_font)

def move_piece(pieces, from_pos, to_pos, symbol):
    if from_pos in pieces and to_pos in ADJACENT[from_pos] and occupied[to_pos] == ' ':
        pieces[pieces.index(from_pos)] = to_pos
        occupied[from_pos] = ' '
        occupied[to_pos] = symbol
        animations.append([symbol, from_pos, to_pos, symbol, 0])
        return True
    return False

def check_win(pieces):
    return any(8 in line and all(p in pieces for p in line) for line in WINNING_LINES)


def ai_turn():
    pygame.time.wait(300)
    for i in ai_pieces:
        for j in ADJACENT[i]:
            if occupied[j] == ' ':
                temp = ai_pieces[:]
                temp[temp.index(i)] = j
                if check_win(temp):
                    move_piece(ai_pieces, i, j, 'O')
                    return
    for i in ai_pieces:
        for j in ADJACENT[i]:
            if occupied[j] == ' ':
                temp = player_pieces[:]
                for k in range(len(temp)):
                    test = temp[:]
                    test[k] = j
                    if check_win(test):
                        move_piece(ai_pieces, i, j, 'O')
                        return
    random.shuffle(ai_pieces)
    for i in ai_pieces:
        random.shuffle(ADJACENT[i])
        for j in ADJACENT[i]:
            if occupied[j] == ' ':
                move_piece(ai_pieces, i, j, 'O')
                return

# Helper to detect hover index
def get_clicked_spot(mouse_pos):
    for i, pos in enumerate(CIRCLE_POSITIONS):
        if math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1]) <= NODE_RADIUS:
            return i
    return None

# Main loop
while True:
    mouse_pos = pygame.mouse.get_pos()
    clicked_spot = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_started and event.type == pygame.MOUSEBUTTONDOWN:
            if 300 <= mouse_pos[0] <= 500 and 250 <= mouse_pos[1] <= 320:
                game_started = True
                reset_game()

        elif game_started and event.type == pygame.MOUSEBUTTONDOWN:
            if WIDTH - 140 <= mouse_pos[0] <= WIDTH - 20 and HEIGHT - 50 <= mouse_pos[1] <= HEIGHT - 15:
                reset_game()
                continue
            if not game_over and turn == 'Player':
                clicked_spot = get_clicked_spot(mouse_pos)
                if clicked_spot is not None:
                    if selected is None:
                        if clicked_spot in player_pieces:
                            selected = clicked_spot
                    else:
                        if move_piece(player_pieces, selected, clicked_spot, 'X'):
                            if check_win(player_pieces):
                                game_over = True
                                winner = 'Player'
                            turn = 'AI'
                        selected = None

    if game_started:
        draw_board(hover=get_clicked_spot(mouse_pos))
        if not game_over and turn == 'AI' and not animations:
            ai_turn()
            if check_win(ai_pieces):
                game_over = True
                winner = 'AI'
            turn = 'Player'
    else:
        screen.fill(BG_COLOR)
        draw_text("Circular Tic Tac Toe", 230, 150, large_font)
        pygame.draw.rect(screen, BUTTON_COLOR, (300, 250, 200, 70))
        draw_text("Play", 380, 270, large_font)

    pygame.display.flip()
    clock.tick(FPS)