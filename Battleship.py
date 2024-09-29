import pygame
import random

# Define constants
WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 550
GRID_SIZE = 10
CELL_SIZE = 45
SHIP_TYPES = [('Battleship', 4), ('Destroyer', 3), ('Submarine', 2)]

# Colors
WATER_COLOR = (0, 0, 255)
SHIP_COLOR = (169, 169, 169)
HIT_COLOR = (255, 0, 0)
MISS_COLOR = (255, 255, 255)
MENU_COLOR = (255, 255, 255)
FEEDBACK_COLOR = (50, 255, 50)
LABEL_COLOR = (255, 255, 255)

pygame.init()

#------------------------------#
#             SHIP             #
#------------------------------#

class Ship:
    def __init__(self, length, orientation, start_pos):
        self.length = length
        self.orientation = orientation
        self.start_pos = start_pos
        self.hits = 0
        self.name = self.get_ship_name()

    def get_ship_name(self):
        if self.length == 4:
            return 'Battleship'
        elif self.length == 3:
            return 'Destroyer'
        elif self.length == 2:
            return 'Submarine'
        return 'Unknown Ship'

    def is_sunk(self):
        return self.hits >= self.length

    def get_coordinates(self):
        coords = []
        x, y = self.start_pos
        if self.orientation == 'H':
            for i in range(self.length):
                coords.append((x + i, y))
        else:
            for i in range(self.length):
                coords.append((x, y + i))
        return coords

#------------------------------#
#            BOARD             #
#------------------------------#

class Board:
    def __init__(self):
        self.grid = [['~' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.ships = []
        self.place_ships()

    def place_ships(self):
        for name, length in SHIP_TYPES:
            self.place_ship_recursively(length)

    def place_ship_recursively(self, ship_length):
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        orientation = random.choice(['H', 'V'])
        if self.can_place_ship(x, y, ship_length, orientation):
            ship = Ship(ship_length, orientation, (x, y))
            self.ships.append(ship)
            self.mark_ship_on_grid(ship)
        else:
            self.place_ship_recursively(ship_length)

    def can_place_ship(self, x, y, length, orientation):
        if orientation == 'H':
            if x + length > GRID_SIZE:
                return False
            for i in range(length):
                if self.grid[y][x + i] != '~':
                    return False
        elif orientation == 'V':
            if y + length > GRID_SIZE:
                return False
            for i in range(length):
                if self.grid[y + i][x] != '~':
                    return False
        return True

    def mark_ship_on_grid(self, ship):
        x, y = ship.start_pos
        if ship.orientation == 'H':
            for i in range(ship.length):
                self.grid[y][x + i] = 'S'
        elif ship.orientation == 'V':
            for i in range(ship.length):
                self.grid[y + i][x] = 'S'

    def attack(self, position):
        x, y = position
        if self.grid[y][x] == 'S':
            self.grid[y][x] = 'X'  # Mark hit
            for ship in self.ships:
                if (x, y) in ship.get_coordinates():
                    ship.hits += 1
                    return 'Hit!', ship.name if ship.is_sunk() else ''
            return 'Hit!', ''
        elif self.grid[y][x] == '~':
            self.grid[y][x] = 'O'  # Mark miss
            return 'Miss!', ''

    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)

    def draw(self, screen, offset, reveal_ships=False):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                rect = pygame.Rect(offset[0] + col * CELL_SIZE, offset[1] + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if reveal_ships and self.grid[row][col] == 'S':
                    pygame.draw.rect(screen, SHIP_COLOR, rect)  # Draw ship if revealing
                elif self.grid[row][col] == 'X':
                    pygame.draw.rect(screen, HIT_COLOR, rect)  # Draw hit
                elif self.grid[row][col] == 'O':
                    pygame.draw.rect(screen, MISS_COLOR, rect)  # Draw miss
                else:
                    pygame.draw.rect(screen, WATER_COLOR, rect)  # Water
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Cell border

#------------------------------#
#            PLAYER            #
#------------------------------#

class Player:
    def __init__(self, name, is_computer=False):
        self.name = name
        self.board = Board()
        self.is_computer = is_computer
        self.score = 0

    def take_turn(self, opponent_board, position=None):
        if self.is_computer:
            return self.computer_turn(opponent_board)
        else:
            return self.human_turn(opponent_board, position)

    def human_turn(self, opponent_board, position):
        if position:
            return opponent_board.attack(position)
        return None

    def computer_turn(self, opponent_board):
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        while opponent_board.grid[y][x] in ['X', 'O']:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        return opponent_board.attack((x, y))

    def update_score(self):
        self.score += 1

#------------------------------#
#             GAME             #
#------------------------------#

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Battleship Game')
        self.clock = pygame.time.Clock()
        self.player = Player(name='Player 1')
        self.computer = Player(name='Computer', is_computer=True)
        self.current_turn = self.player
        self.menu_active = True
        self.credits_active = False
        self.player_feedback = ""
        self.computer_feedback = ""
        self.player_sunk_feedback = ""
        self.computer_sunk_feedback = ""

    def run(self):
        while True:
            if self.menu_active:
                self.show_menu()
            elif self.credits_active:
                self.show_credits()
            else:
                self.handle_events()
                self.draw()
                self.check_game_over()
                pygame.display.flip()
                self.clock.tick(30)

    def show_menu(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 55)
        play_text = font.render('Play', True, MENU_COLOR)
        credits_text = font.render('Credits', True, MENU_COLOR)
        exit_text = font.render('Exit', True, MENU_COLOR)

        self.screen.blit(play_text, (WINDOW_WIDTH // 2 - play_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(credits_text, (WINDOW_WIDTH // 2 - credits_text.get_width() // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(exit_text, (WINDOW_WIDTH // 2 - exit_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60))

        pygame.display.flip()
        self.handle_menu_events()

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.is_play_button_clicked(mouse_pos):
                    self.menu_active = False
                    self.credits_active = False  
                elif self.is_credits_button_clicked(mouse_pos):
                    self.credits_active = True
                    self.menu_active = False
                elif self.is_exit_button_clicked(mouse_pos):
                    pygame.quit()
                    exit()

    def is_play_button_clicked(self, pos):
        return (WINDOW_WIDTH // 2 - 70 < pos[0] < WINDOW_WIDTH // 2 + 70 and
                WINDOW_HEIGHT // 2 - 60 < pos[1] < WINDOW_HEIGHT // 2)

    def is_credits_button_clicked(self, pos):
        return (WINDOW_WIDTH // 2 - 70 < pos[0] < WINDOW_WIDTH // 2 + 70 and
                WINDOW_HEIGHT // 2 < pos[1] < WINDOW_HEIGHT // 2 + 60)

    def is_exit_button_clicked(self, pos):
        return (WINDOW_WIDTH // 2 - 70 < pos[0] < WINDOW_WIDTH // 2 + 70 and
                WINDOW_HEIGHT // 2 + 60 < pos[1] < WINDOW_HEIGHT // 2 + 120)

    def show_credits(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 55)
        credits_text = font.render('Credits', True, MENU_COLOR)
        author_text = font.render('Created by James A.', True, MENU_COLOR)
        back_text = font.render('Back', True, MENU_COLOR)

        self.screen.blit(credits_text, (WINDOW_WIDTH // 2 - credits_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(author_text, (WINDOW_WIDTH // 2 - author_text.get_width() // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(back_text, (WINDOW_WIDTH // 2 - back_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60))

        pygame.display.flip()
        self.handle_credits_events()

    def handle_credits_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.is_back_button_clicked(mouse_pos):
                    self.credits_active = False  
                    self.menu_active = True  

    def is_back_button_clicked(self, pos):
        return (WINDOW_WIDTH // 2 - 70 < pos[0] < WINDOW_WIDTH // 2 + 70 and
                WINDOW_HEIGHT // 2 + 60 < pos[1] < WINDOW_HEIGHT // 2 + 120)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.current_turn.is_computer:
                    self.handle_player_turn(event.pos)

    def handle_player_turn(self, pos):
        self.player_sunk_feedback = ""
        self.computer_sunk_feedback = ""
        x = (pos[0] - 550) // CELL_SIZE
        y = (pos[1] - 50) // CELL_SIZE
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            if self.computer.board.grid[y][x] not in ['X', 'O']:
                feedback, sunk_name = self.current_turn.take_turn(self.computer.board, (x, y))
                self.player_feedback = feedback
                if sunk_name:
                    self.player_sunk_feedback = f'You sunk my {sunk_name}!'
                self.current_turn = self.computer  # Switch to computer's turn
                self.computer_turn()

    def computer_turn(self):
        feedback, sunk_name = self.current_turn.take_turn(self.player.board)
        self.computer_feedback = feedback
        if sunk_name:
            self.computer_sunk_feedback = f'Your {sunk_name} has been destroyed!'
        self.current_turn = self.player  # Switch back to player's turn

    def check_game_over(self):
        if self.player.board.all_ships_sunk():
            self.show_winner('Computer')
        elif self.computer.board.all_ships_sunk():
            self.show_winner('Player')

    def show_winner(self, winner):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 55)
        winner_text = font.render(f'{winner} Wins!', True, MENU_COLOR)
        restart_text = font.render('Restart', True, MENU_COLOR)
        exit_text = font.render('Exit', True, MENU_COLOR)

        self.screen.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(exit_text, (WINDOW_WIDTH // 2 - exit_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60))

        pygame.display.flip()

        # Clear the event queue before waiting for new events
        pygame.event.clear()
        self.handle_winner_events()

    def handle_winner_events(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.is_restart_button_clicked(mouse_pos):
                        self.reset_game()
                        waiting = False  # Exit the waiting loop
                    elif self.is_exit_button_clicked(mouse_pos):
                        pygame.quit()
                        exit()

    def is_restart_button_clicked(self, pos):
        return (WINDOW_WIDTH // 2 - 70 < pos[0] < WINDOW_WIDTH // 2 + 70 and
                WINDOW_HEIGHT // 2 < pos[1] < WINDOW_HEIGHT // 2 + 60)

    def reset_game(self):
        self.player = Player(name='Player 1')
        self.computer = Player(name='Computer', is_computer=True)
        self.current_turn = self.player
        self.player_feedback = ""
        self.computer_feedback = ""
        self.player_sunk_feedback = ""
        self.computer_sunk_feedback = ""

    def draw_feedback(self):
        font = pygame.font.SysFont(None, 48)

        # Draw player's feedback centered above the player's grid
        player_feedback_text = font.render(self.player_feedback, True, FEEDBACK_COLOR)
        self.screen.blit(player_feedback_text, ((GRID_SIZE * CELL_SIZE) / 2 + 550 - player_feedback_text.get_width() // 2, 10))

        # Draw computer's feedback centered above the computer's grid
        computer_feedback_text = font.render(self.computer_feedback, True, FEEDBACK_COLOR)
        self.screen.blit(computer_feedback_text, ((GRID_SIZE * CELL_SIZE) / 2 + 50 - computer_feedback_text.get_width() // 2, 10))

        # Draw player's sunk feedback on the right side
        if self.player_sunk_feedback:
            player_sunk_feedback_text = font.render(self.player_sunk_feedback, True, FEEDBACK_COLOR)
            self.screen.blit(player_sunk_feedback_text, (WINDOW_WIDTH - player_sunk_feedback_text.get_width() - 20, WINDOW_HEIGHT - 40))

        # Draw computer's sunk feedback on the left side
        if self.computer_sunk_feedback:
            computer_sunk_feedback_text = font.render(self.computer_sunk_feedback, True, FEEDBACK_COLOR)
            self.screen.blit(computer_sunk_feedback_text, (20, WINDOW_HEIGHT - 40))

        # Draw labels for Player and Computer
        label_font = pygame.font.SysFont(None, 36)
        player_label = label_font.render('Player', True, LABEL_COLOR)
        computer_label = label_font.render('Computer', True, LABEL_COLOR)

        self.screen.blit(player_label, (95 - player_label.get_width() // 2, 10))
        self.screen.blit(computer_label, (615 - computer_label.get_width() // 2, 10))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.player.board.draw(self.screen, offset=(50, 50), reveal_ships=True)
        self.computer.board.draw(self.screen, offset=(550, 50), reveal_ships=False)

        self.draw_feedback()  # Draw feedback messages

# Main execution
if __name__ == '__main__':
    game = Game()
    game.run()