import pygame
import random
from collections import deque

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):   # <-- fixed (was _init_)
        self.reset()
        
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow_pending = 2  # Start with length 3
        
    def get_head_position(self):
        return self.positions[0]
    
    def turn(self, point):
        if len(self.positions) > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        self.direction = point
    
    def move(self):
        head = self.get_head_position()
        x, y = self.direction
        new_position = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        if new_position in self.positions[1:]:
            return False
            
        self.positions.insert(0, new_position)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
            
        return True
    
    def grow(self):
        self.grow_pending += 1
    
    def draw(self, surface):
        for i, p in enumerate(self.positions):
            color = GREEN if i == 0 else BLUE
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)

class Food:
    def __init__(self):   # <-- fixed (was _init_)
        self.position = (0, 0)
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, RED, rect)

class SnakeAI:
    def __init__(self, snake, food):   # <-- fixed (was _init_)
        self.snake = snake
        self.food = food
        
    def get_next_move(self):
        # Simple BFS to find path to food
        start = self.snake.get_head_position()
        target = self.food.position
        
        if start == target:
            return self.snake.direction
            
        queue = deque([start])
        visited = {start: None}
        
        while queue:
            current = queue.popleft()
            
            for direction in [UP, DOWN, LEFT, RIGHT]:
                neighbor = ((current[0] + direction[0]) % GRID_WIDTH, 
                           (current[1] + direction[1]) % GRID_HEIGHT)
                
                if neighbor in visited or neighbor in self.snake.positions[:-1]:
                    continue
                    
                visited[neighbor] = current
                queue.append(neighbor)
                
                if neighbor == target:
                    # Reconstruct path to find first move
                    while visited[neighbor] != start:
                        neighbor = visited[neighbor]
                    return (neighbor[0] - start[0], neighbor[1] - start[1])
        
        # If no path found, move randomly to avoid collision
        head = self.snake.get_head_position()
        safe_moves = []
        
        for direction in [UP, DOWN, LEFT, RIGHT]:
            new_pos = ((head[0] + direction[0]) % GRID_WIDTH, 
                      (head[1] + direction[1]) % GRID_HEIGHT)
            
            if new_pos not in self.snake.positions[:-1]:
                safe_moves.append(direction)
        
        return safe_moves[0] if safe_moves else self.snake.direction

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake AI')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 20)
    
    snake = Snake()
    food = Food()
    ai = SnakeAI(snake, food)
    
    # Ensure food doesn't spawn on snake initially
    while food.position in snake.positions:
        food.randomize_position()
    
    running = True
    game_over = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    snake.reset()
                    food.randomize_position()
                    game_over = False
        
        if not game_over:
            # AI makes the move
            next_move = ai.get_next_move()
            snake.turn(next_move)
            
            # Move snake and check game over
            if not snake.move():
                game_over = True
            
            # Check if food eaten
            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position()
                while food.position in snake.positions:
                    food.randomize_position()
        
        # Draw everything
        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)
        
        # Display score
        score_text = font.render(f'Score: {len(snake.positions) - 1}', True, GREEN)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            game_over_text = font.render('Game Over - Press R to restart', True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":   # <-- fixed (was "_main_")
    main()
