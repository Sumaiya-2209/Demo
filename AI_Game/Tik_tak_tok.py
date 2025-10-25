import pygame
import sys
import numpy as np

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
LINE_WIDTH = 15
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
WIN_LINE_COLOR_X = (80, 80, 80)
WIN_LINE_COLOR_O = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe AI')
screen.fill(BG_COLOR)

# Board
board = np.zeros((BOARD_ROWS, BOARD_COLS))

# Font for displaying messages
END_FONT = pygame.font.SysFont('arial', 70)

# Draw lines
def draw_lines():
    # Horizontal lines
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    # Vertical lines
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

# Draw figures
def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:  # Circle (player)
                pygame.draw.circle(
                    screen,
                    CIRCLE_COLOR,
                    (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)),
                    CIRCLE_RADIUS,
                    CIRCLE_WIDTH
                )
            elif board[row][col] == 2:  # Cross (AI)
                pygame.draw.line(
                    screen,
                    CROSS_COLOR,
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE),
                    CROSS_WIDTH
                )
                pygame.draw.line(
                    screen,
                    CROSS_COLOR,
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    CROSS_WIDTH
                )

# Mark square
def mark_square(row, col, player):
    board[row][col] = player

# Check if square is available
def is_square_empty(row, col):
    return board[row][col] == 0

# Check if board is full
def is_board_full():
    return not np.any(board == 0)

# Check for win
def check_win(player):
    # Vertical win check
    for col in range(BOARD_COLS):
        if all(board[row][col] == player for row in range(BOARD_ROWS)):
            draw_vertical_winning_line(col, player)
            return True
    # Horizontal win check
    for row in range(BOARD_ROWS):
        if all(board[row][col] == player for col in range(BOARD_COLS)):
            draw_horizontal_winning_line(row, player)
            return True
    # Diagonal win check
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        draw_asc_diagonal(player)
        return True
    if board[0][2] == player and board[1][1] == player and board[2][0] == player:
        draw_desc_diagonal(player)
        return True
    return False

# Functions to draw the winning line
def draw_vertical_winning_line(col, player):
    posX = col * SQUARE_SIZE + SQUARE_SIZE // 2
    color = WIN_LINE_COLOR_O if player == 1 else WIN_LINE_COLOR_X
    pygame.draw.line(screen, color, (posX, 15), (posX, HEIGHT - 15), 15)

def draw_horizontal_winning_line(row, player):
    posY = row * SQUARE_SIZE + SQUARE_SIZE // 2
    color = WIN_LINE_COLOR_O if player == 1 else WIN_LINE_COLOR_X
    pygame.draw.line(screen, color, (15, posY), (WIDTH - 15, posY), 15)

def draw_asc_diagonal(player):
    color = WIN_LINE_COLOR_O if player == 1 else WIN_LINE_COLOR_X
    pygame.draw.line(screen, color, (15, 15), (WIDTH - 15, HEIGHT - 15), 25)

def draw_desc_diagonal(player):
    color = WIN_LINE_COLOR_O if player == 1 else WIN_LINE_COLOR_X
    pygame.draw.line(screen, color, (15, HEIGHT - 15), (WIDTH - 15, 15), 25)

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, is_maximizing, alpha, beta):
    if check_win_for_minimax(2): return 1
    elif check_win_for_minimax(1): return -1
    elif is_board_full(): return 0
    
    if is_maximizing:
        best_score = -np.inf
        for r, c in np.argwhere(board == 0):
            board[r, c] = 2
            score = minimax(board, depth + 1, False, alpha, beta)
            board[r, c] = 0
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            if beta <= alpha: break
        return best_score
    else:
        best_score = np.inf
        for r, c in np.argwhere(board == 0):
            board[r, c] = 1
            score = minimax(board, depth + 1, True, alpha, beta)
            board[r, c] = 0
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            if beta <= alpha: break
        return best_score

# Helper function for minimax to avoid drawing lines
def check_win_for_minimax(player):
    for col in range(BOARD_COLS):
        if all(board[row][col] == player for row in range(BOARD_ROWS)): return True
    for row in range(BOARD_ROWS):
        if all(board[row][col] == player for col in range(BOARD_COLS)): return True
    if board[0][0] == player and board[1][1] == player and board[2][2] == player: return True
    if board[0][2] == player and board[1][1] == player and board[2][0] == player: return True
    return False

# AI's move using minimax
def ai_move():
    best_score = -np.inf
    best_move = None
    for r, c in np.argwhere(board == 0):
        board[r, c] = 2
        score = minimax(board, 0, False, -np.inf, np.inf)
        board[r, c] = 0
        if score > best_score:
            best_score = score
            best_move = (r, c)
    if best_move:
        mark_square(best_move[0], best_move[1], 2)
        return True
    return False

# Restart game
def restart():
    screen.fill(BG_COLOR)
    draw_lines()
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = 0
    pygame.display.update()

# Function to draw the end game message
def draw_end_message(winner):
    if winner == 1: text = "You Win!"
    elif winner == 2: text = "AI Wins!"
    else: text = "Tie Game"
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((40, 40, 40, 150))
    screen.blit(overlay, (0, 0))
    
    end_text = END_FONT.render(text, True, (255, 255, 255))
    text_rect = end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(end_text, text_rect)
    print(f"Game Over: {text}")

# Main game loop (modified for instant win line then message)
def main():
    draw_lines()
    player = 1
    game_over = False
    winner = None
    end_shown = False  # prevent drawing the end message multiple times

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart()
                    player = 1
                    game_over = False
                    winner = None
                    end_shown = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if player == 1:
                    mouseX, mouseY = event.pos
                    clicked_row = int(mouseY // SQUARE_SIZE)
                    clicked_col = int(mouseX // SQUARE_SIZE)
                    
                    if is_square_empty(clicked_row, clicked_col):
                        mark_square(clicked_row, clicked_col, player)
                        draw_figures()
                        pygame.display.update()  # show player's move

                        if check_win(player):
                            pygame.display.update()     # show the winning line immediately
                            pygame.time.delay(600)      # small pause
                            winner = player
                            draw_end_message(winner)    # show final message once
                            pygame.display.update()
                            game_over = True
                            end_shown = True
                        elif is_board_full():
                            winner = 0
                            draw_end_message(winner)
                            pygame.display.update()
                            game_over = True
                            end_shown = True
                        else:
                            player = 2

        if not game_over and player == 2:
            pygame.time.delay(500)  # AI 'thinking' delay
            if ai_move():
                draw_figures()
                pygame.display.update()  # show AI's move

                if check_win(2):
                    pygame.display.update()     # show the winning line immediately
                    pygame.time.delay(600)      # small pause
                    winner = 2
                    draw_end_message(winner)    # show final message once
                    pygame.display.update()
                    game_over = True
                    end_shown = True
                elif is_board_full():
                    winner = 0
                    draw_end_message(winner)
                    pygame.display.update()
                    game_over = True
                    end_shown = True
                else:
                    player = 1
        
        # Just keep updating the screen; end message is drawn once above.
        pygame.display.update()

if __name__ == "__main__":
    main()