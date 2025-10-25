import pygame
import sys
import copy
from enum import Enum
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 680  # Increased height for status area
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)
HIGHLIGHT = (100, 249, 83, 150)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
STATUS_BG = (240, 240, 240)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess with AI")
clock = pygame.time.Clock()

# Try to load fonts that support chess symbols
def get_chess_font(size):
    chess_fonts = [
        'Segoe UI Symbol',
        'Arial Unicode MS',
        'DejaVu Sans',
        'FreeSerif',
        'Quivira',
        'Code2000',
        'Lucida Sans Unicode',
        'Times New Roman'
    ]
    for font_name in chess_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            # Test if the font supports chess symbols by rendering a king
            test_surface = font.render('♔', True, BLACK)
            if test_surface.get_width() > 0:
                return font
        except:
            continue
    # Fallback to default font with text representations
    return pygame.font.SysFont('Arial', size)

# Chess piece Unicode symbols with fallback text
class PieceType(Enum):
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6

class PieceColor(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    def __init__(self, piece_type, color):
        self.piece_type = piece_type
        self.color = color
        self.has_moved = False

    def get_symbol(self):
        symbols_white = {
            PieceType.KING: '♔',
            PieceType.QUEEN: '♕',
            PieceType.ROOK: '♖',
            PieceType.BISHOP: '♗',
            PieceType.KNIGHT: '♘',
            PieceType.PAWN: '♙'
        }
        symbols_black = {
            PieceType.KING: '♚',
            PieceType.QUEEN: '♛',
            PieceType.ROOK: '♜',
            PieceType.BISHOP: '♝',
            PieceType.KNIGHT: '♞',
            PieceType.PAWN: '♟'
        }

        if self.color == PieceColor.WHITE:
            return symbols_white[self.piece_type]
        else:
            return symbols_black[self.piece_type]

    def get_text_fallback(self):
        text_white = {
            PieceType.KING: 'K',
            PieceType.QUEEN: 'Q',
            PieceType.ROOK: 'R',
            PieceType.BISHOP: 'B',
            PieceType.KNIGHT: 'N',
            PieceType.PAWN: 'P'
        }
        text_black = {
            PieceType.KING: 'k',
            PieceType.QUEEN: 'q',
            PieceType.ROOK: 'r',
            PieceType.BISHOP: 'b',
            PieceType.KNIGHT: 'n',
            PieceType.PAWN: 'p'
        }

        if self.color == PieceColor.WHITE:
            return text_white[self.piece_type]
        else:
            return text_black[self.piece_type]

    def get_name(self):
        names = {
            PieceType.KING: 'King',
            PieceType.QUEEN: 'Queen',
            PieceType.ROOK: 'Rook',
            PieceType.BISHOP: 'Bishop',
            PieceType.KNIGHT: 'Knight',
            PieceType.PAWN: 'Pawn'
        }
        return names[self.piece_type]

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_piece = None
        self.valid_moves = []
        self.turn = PieceColor.WHITE
        self.game_over = False
        self.winner = None
        self.check = False
        self.setup_board()

    def setup_board(self):
        # Clear the board
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Set up pawns
        for col in range(BOARD_SIZE):
            self.board[1][col] = Piece(PieceType.PAWN, PieceColor.BLACK)
            self.board[6][col] = Piece(PieceType.PAWN, PieceColor.WHITE)

        # Set up other pieces
        back_row = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                   PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]

        for col, piece_type in enumerate(back_row):
            self.board[0][col] = Piece(piece_type, PieceColor.BLACK)
            self.board[7][col] = Piece(piece_type, PieceColor.WHITE)

    def get_piece(self, row, col):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

    def select_piece(self, row, col):
        piece = self.get_piece(row, col)
        if piece and piece.color == self.turn:
            self.selected_piece = (row, col)
            self.valid_moves = self.get_valid_moves(row, col)
            return True
        return False

    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False

        # Check if the move is valid
        if (to_row, to_col) not in self.get_valid_moves(from_row, from_col):
            return False

        # Make the move
        captured_piece = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True

        # Check for pawn promotion
        if piece.piece_type == PieceType.PAWN:
            if (piece.color == PieceColor.WHITE and to_row == 0) or \
               (piece.color == PieceColor.BLACK and to_row == 7):
                self.board[to_row][to_col] = Piece(PieceType.QUEEN, piece.color)

        # Switch turns
        self.turn = PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE

        # Check for check and checkmate
        self.check = self.is_in_check(self.turn)
        if self.is_checkmate(self.turn):
            self.game_over = True
            self.winner = PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE

        return True

    def get_valid_moves(self, row, col):
        piece = self.get_piece(row, col)
        if not piece:
            return []

        moves = []

        if piece.piece_type == PieceType.PAWN:
            moves = self.get_pawn_moves(row, col, piece)
        elif piece.piece_type == PieceType.ROOK:
            moves = self.get_rook_moves(row, col, piece)
        elif piece.piece_type == PieceType.KNIGHT:
            moves = self.get_knight_moves(row, col, piece)
        elif piece.piece_type == PieceType.BISHOP:
            moves = self.get_bishop_moves(row, col, piece)
        elif piece.piece_type == PieceType.QUEEN:
            moves = self.get_queen_moves(row, col, piece)
        elif piece.piece_type == PieceType.KING:
            moves = self.get_king_moves(row, col, piece)

        # Filter out moves that would put or leave the king in check
        valid_moves = []
        for move in moves:
            if not self.would_be_in_check(row, col, move[0], move[1], piece.color):
                valid_moves.append(move)

        return valid_moves

    def get_pawn_moves(self, row, col, piece):
        moves = []
        direction = -1 if piece.color == PieceColor.WHITE else 1

        # Move forward one square
        if self.get_piece(row + direction, col) is None:
            moves.append((row + direction, col))

            # Move forward two squares from starting position
            if not piece.has_moved and self.get_piece(row + 2 * direction, col) is None:
                moves.append((row + 2 * direction, col))

        # Capture diagonally
        for offset in [-1, 1]:
            target_piece = self.get_piece(row + direction, col + offset)
            if target_piece and target_piece.color != piece.color:
                moves.append((row + direction, col + offset))

        return moves

    def get_rook_moves(self, row, col, piece):
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = row + i * dr, col + i * dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break

                target_piece = self.get_piece(r, c)
                if target_piece is None:
                    moves.append((r, c))
                elif target_piece.color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break

        return moves

    def get_knight_moves(self, row, col, piece):
        moves = []
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = self.get_piece(r, c)
                if target_piece is None or target_piece.color != piece.color:
                    moves.append((r, c))

        return moves

    def get_bishop_moves(self, row, col, piece):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = row + i * dr, col + i * dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break

                target_piece = self.get_piece(r, c)
                if target_piece is None:
                    moves.append((r, c))
                elif target_piece.color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break

        return moves

    def get_queen_moves(self, row, col, piece):
        return self.get_rook_moves(row, col, piece) + self.get_bishop_moves(row, col, piece)

    def get_king_moves(self, row, col, piece):
        moves = []
        king_moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = self.get_piece(r, c)
                if target_piece is None or target_piece.color != piece.color:
                    moves.append((r, c))

        return moves

    def would_be_in_check(self, from_row, from_col, to_row, to_col, color):
        # Create a simulated board (deep copy)
        temp_board = copy.deepcopy(self.board)

        # Make the simulated move
        temp_board[to_row][to_col] = temp_board[from_row][from_col]
        temp_board[from_row][from_col] = None

        # Find the king on the simulated board
        king_pos = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = temp_board[r][c]
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        if not king_pos:
            # No king found (shouldn't happen in normal play) -> not considered in check here
            return False

        opponent_color = PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE

        # Check if any opponent piece attacks the king on the simulated board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = temp_board[r][c]
                if piece and piece.color == opponent_color:
                    moves = self.get_valid_moves_simulated(r, c, piece, temp_board)
                    if king_pos in moves:
                        return True
        return False

    def get_valid_moves_simulated(self, row, col, piece, board):
        if piece.piece_type == PieceType.PAWN:
            return self.get_pawn_moves_simulated(row, col, piece, board)
        elif piece.piece_type == PieceType.ROOK:
            return self.get_rook_moves_simulated(row, col, piece, board)
        elif piece.piece_type == PieceType.KNIGHT:
            return self.get_knight_moves_simulated(row, col, piece, board)
        elif piece.piece_type == PieceType.BISHOP:
            return self.get_bishop_moves_simulated(row, col, piece, board)
        elif piece.piece_type == PieceType.QUEEN:
            return self.get_queen_moves_simulated(row, col, piece, board)
        elif piece.piece_type == PieceType.KING:
            return self.get_king_moves_simulated(row, col, piece, board)
        return []

    def get_pawn_moves_simulated(self, row, col, piece, board):
        moves = []
        direction = -1 if piece.color == PieceColor.WHITE else 1

        if self.get_piece_simulated(row + direction, col, board) is None:
            moves.append((row + direction, col))
            if not piece.has_moved and self.get_piece_simulated(row + 2 * direction, col, board) is None:
                moves.append((row + 2 * direction, col))

        for offset in [-1, 1]:
            target_piece = self.get_piece_simulated(row + direction, col + offset, board)
            if target_piece and target_piece.color != piece.color:
                moves.append((row + direction, col + offset))
        return moves

    def get_rook_moves_simulated(self, row, col, piece, board):
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = row + i * dr, col + i * dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                target_piece = self.get_piece_simulated(r, c, board)
                if target_piece is None:
                    moves.append((r, c))
                elif target_piece.color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

    def get_knight_moves_simulated(self, row, col, piece, board):
        moves = []
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = self.get_piece_simulated(r, c, board)
                if target_piece is None or target_piece.color != piece.color:
                    moves.append((r, c))
        return moves

    def get_bishop_moves_simulated(self, row, col, piece, board):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = row + i * dr, col + i * dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                target_piece = self.get_piece_simulated(r, c, board)
                if target_piece is None:
                    moves.append((r, c))
                elif target_piece.color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

    def get_queen_moves_simulated(self, row, col, piece, board):
        return self.get_rook_moves_simulated(row, col, piece, board) + self.get_bishop_moves_simulated(row, col, piece, board)

    def get_king_moves_simulated(self, row, col, piece, board):
        moves = []
        king_moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = self.get_piece_simulated(r, c, board)
                if target_piece is None or target_piece.color != piece.color:
                    moves.append((r, c))
        return moves

    def get_piece_simulated(self, row, col, board):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return board[row][col]
        return None

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.get_piece(r, c)
                if piece and piece.color == color:
                    if self.get_valid_moves(r, c):
                        return False
        return True

    def is_in_check(self, color):
        king_pos = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.get_piece(r, c)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if not king_pos:
            return False
        opponent_color = PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.get_piece(r, c)
                if piece and piece.color == opponent_color:
                    if king_pos in self.get_valid_moves(r, c):
                        return True
        return False

class ChessAI:
    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.depth = 2

    def get_move(self):
        _, move = self.minimax(self.depth, -float('inf'), float('inf'), True)
        if move is None:
            moves = self.get_all_moves(self.color)
            if moves:
                return moves[0]
            return None
        return move

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.board.game_over:
            return self.evaluate_board(), None

        if maximizing_player:
            max_eval = -float('inf')
            best_move = None
            for move in self.get_all_moves(self.color):
                from_row, from_col, to_row, to_col = move
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)

                # simulate move
                self.board.board[to_row][to_col] = piece
                self.board.board[from_row][from_col] = None

                eval, _ = self.minimax(depth - 1, alpha, beta, False)

                # undo move
                self.board.board[from_row][from_col] = piece
                self.board.board[to_row][to_col] = captured_piece

                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            opponent_color = PieceColor.BLACK if self.color == PieceColor.WHITE else PieceColor.WHITE
            for move in self.get_all_moves(opponent_color):
                from_row, from_col, to_row, to_col = move
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)

                # simulate move
                self.board.board[to_row][to_col] = piece
                self.board.board[from_row][from_col] = None

                eval, _ = self.minimax(depth - 1, alpha, beta, True)

                # undo move
                self.board.board[from_row][from_col] = piece
                self.board.board[to_row][to_col] = captured_piece

                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_all_moves(self, color):
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board.get_piece(r, c)
                if piece and piece.color == color:
                    valid_moves = self.board.get_valid_moves(r, c)
                    for move in valid_moves:
                        moves.append((r, c, move[0], move[1]))
        return moves

    def evaluate_board(self):
        score = 0
        piece_values = {
            PieceType.PAWN: 10,
            PieceType.KNIGHT: 30,
            PieceType.BISHOP: 30,
            PieceType.ROOK: 50,
            PieceType.QUEEN: 90,
            PieceType.KING: 900
        }

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board.get_piece(r, c)
                if piece:
                    value = piece_values[piece.piece_type]
                    if piece.color == self.color:
                        score += value
                    else:
                        score -= value

        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for r, c in center_squares:
            piece = self.board.get_piece(r, c)
            if piece and piece.color == self.color:
                score += 5
            elif piece and piece.color != self.color:
                score -= 5
        return score

# Global variable to track if Unicode symbols work
unicode_symbols_work = True

def test_unicode_support():
    """Test if Unicode chess symbols work with available fonts"""
    global unicode_symbols_work
    test_font = get_chess_font(48)
    test_surface = test_font.render('♔', True, BLACK)
    unicode_symbols_work = test_surface.get_width() > 5  # More reliable test

def draw_board():
    # Draw chess board squares
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Draw coordinates
            font_small = pygame.font.SysFont('Arial', 14)
            if row == 7:  # File letters at bottom
                file_letter = chr(97 + col)  # a-h
                text = font_small.render(file_letter, True, BLACK if (row + col) % 2 == 0 else WHITE)
                screen.blit(text, (col * SQUARE_SIZE + 5, row * SQUARE_SIZE + SQUARE_SIZE - 15))
            if col == 0:  # Rank numbers on left
                rank_number = str(8 - row)
                text = font_small.render(rank_number, True, BLACK if (row + col) % 2 == 0 else WHITE)
                screen.blit(text, (col * SQUARE_SIZE + 5, row * SQUARE_SIZE + 5))

def draw_pieces(board):
    font = get_chess_font(48)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board.get_piece(row, col)
            if piece:
                # white pieces drawn as white text on dark squares and black on light for readability
                text_color = WHITE if piece.color == PieceColor.WHITE else BLACK

                if unicode_symbols_work:
                    symbol = piece.get_symbol()
                else:
                    symbol = piece.get_text_fallback()

                text = font.render(symbol, True, text_color)
                text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                 row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(text, text_rect)

def draw_highlights(board):
    if board.selected_piece:
        sel_row, sel_col = board.selected_piece
        # Highlight selected piece
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 0, 100))  # Yellow highlight
        screen.blit(highlight_surface, (sel_col * SQUARE_SIZE, sel_row * SQUARE_SIZE))

        # Highlight valid moves
        for move in board.valid_moves:
            m_row, m_col = move
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill((0, 255, 0, 100))  # Green highlight for moves
            screen.blit(highlight_surface, (m_col * SQUARE_SIZE, m_row * SQUARE_SIZE))

def draw_status_bar(board):
    # Draw status bar background
    status_rect = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)
    pygame.draw.rect(screen, STATUS_BG, status_rect)
    pygame.draw.line(screen, BLACK, (0, HEIGHT - 40), (WIDTH, HEIGHT - 40), 2)

    font = pygame.font.SysFont('Arial', 20)

    # Turn indicator
    turn_text = "White's Turn" if board.turn == PieceColor.WHITE else "Black's Turn (AI)"
    turn_color = BLUE if board.turn == PieceColor.WHITE else RED
    text = font.render(turn_text, True, turn_color)
    screen.blit(text, (10, HEIGHT - 30))

    # Game status
    status_text = ""
    if board.game_over:
        winner = "White" if board.winner == PieceColor.WHITE else "Black"
        status_text = f"Checkmate! {winner} wins!"
    elif board.check:
        status_text = "Check!"

    if status_text:
        text = font.render(status_text, True, RED)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT - 30))

    # Symbol status
    symbol_status = "Using Unicode symbols" if unicode_symbols_work else "Using text symbols"
    text = font.render(symbol_status, True, GREEN if unicode_symbols_work else RED)
    screen.blit(text, (WIDTH - 240, HEIGHT - 30))

def draw_game_over(board):
    if board.game_over:
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont('Arial', 48)
        font_small = pygame.font.SysFont('Arial', 24)

        winner = "White" if board.winner == PieceColor.WHITE else "Black"
        text = font_large.render(f"{winner} Wins!", True, GREEN)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        screen.blit(text, text_rect)

        restart_text = font_small.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        screen.blit(restart_text, restart_rect)

def main():
    # Test Unicode support at startup
    test_unicode_support()

    board = ChessBoard()
    ai = ChessAI(board, PieceColor.BLACK)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and board.game_over:
                    # Restart game
                    board = ChessBoard()
                    ai = ChessAI(board, PieceColor.BLACK)

            if not board.game_over and board.turn == PieceColor.WHITE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE

                    # Only process clicks on the board (not status area)
                    if row < BOARD_SIZE:
                        if board.selected_piece:
                            from_row, from_col = board.selected_piece
                            if board.move_piece(from_row, from_col, row, col):
                                board.selected_piece = None
                                board.valid_moves = []
                            else:
                                if board.select_piece(row, col):
                                    pass
                                else:
                                    board.selected_piece = None
                                    board.valid_moves = []
                        else:
                            board.select_piece(row, col)

        # AI move
        if not board.game_over and board.turn == PieceColor.BLACK:
            move = ai.get_move()
            if move:
                from_row, from_col, to_row, to_col = move
                board.move_piece(from_row, from_col, to_row, to_col)

        # Draw everything
        screen.fill(WHITE)
        draw_board()
        draw_highlights(board)
        draw_pieces(board)
        draw_status_bar(board)
        draw_game_over(board)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
