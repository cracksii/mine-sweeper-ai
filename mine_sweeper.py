import pygame
import random
import time


class Cell(pygame.Rect):
    def __init__(self, is_bomb: bool, _x, _y, width, height, interface, x_idx, y_idx):
        super().__init__(_x, _y, width, height)
        self.interface = interface
        self.is_bomb = is_bomb
        self.marked = False
        self.looked_up = False
        self.neighbours = -1
        self.default_color = (100, 100, 100)
        self.bomb_color = (255, 255, 128)
        self.text_color = (0, 0, 0)
        self.debug = False
        self.x_idx, self.y_idx = x_idx, y_idx

    def draw(self, num=None, color=None):
        if self.is_bomb and self.debug and not color and not num:
            pygame.draw.rect(self.interface.screen, self.bomb_color, self, border_radius=2)
        elif color:
            pygame.draw.rect(self.interface.screen, color, self, border_radius=2)
        elif num is not None:
            try:
                pygame.draw.rect(self.interface.screen,
                                 ((int(num) * 750 // 18), 100, 133),
                                 self, border_radius=2)
            except ValueError:
                pass
        else:
            pygame.draw.rect(self.interface.screen, self.default_color, self, border_radius=2)
        pygame.display.update()

    def draw_number(self, num):
        self.neighbours = num
        if self.interface.field_size >= 35:
            num = str(num)
            font = pygame.font.SysFont("Comic Sans MS", 25)
            text = font.render(num, False, self.text_color)
            self.interface.screen.blit(text, (self.x + 15, self.y))
            pygame.display.update()


class PyGameInterface:
    def __init__(self, caption, bomb_count, x_fields, y_fields, game, cell_size=40, screen=None):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(caption)
        program_icon = pygame.image.load("Bomb.png")
        pygame.display.set_icon(program_icon)
        self.field_size = cell_size
        self.game = game
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Locks window to th top left of the screen
        self.screen = pygame.display.set_mode([(x_fields + 2) * self.field_size + x_fields, (y_fields + 2)
                                               * self.field_size + y_fields]) if not screen else screen
        self.draw_screen((125, 125, 125))  # fills the screen white
        self.bomb_count = bomb_count
        self.x_fields, self.y_fields = x_fields, y_fields
        self.cells = [[] for _ in range(self.y_fields)]
        self.generator = [False for _ in range((self.x_fields * self.y_fields) - self.bomb_count)]
        self.generator += [True for _ in range(self.bomb_count)]

    def draw_screen(self, color=(255, 255, 255)):
        self.screen.fill(color)
        pygame.display.update()

    def draw_cell(self, multiplier_x=1, multiplier_y=1, color=None, bomb=None, only_create=False):
        if bomb is None:
            bomb = random.choice(self.generator)
            self.generator.remove(bomb)
        rect = Cell(bomb, (self.field_size + 1) * multiplier_x, (self.field_size + 1) * multiplier_y, self.field_size,
                    self.field_size, self, multiplier_x - 1, multiplier_y - 1)
        self.cells[multiplier_y - 1].append(rect)
        if not only_create:
            rect.draw(color=color)

    def draw_cell_pos(self, _x, _y, color=(100, 100, 100)):
        rect = pygame.Rect(_y, _y, 40, 40)
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.display.update()

    def draw_field(self, color=None, is_bomb=None, show_grid=True):
        for i in range(self.y_fields):
            for j in range(self.x_fields):
                if color:
                    self.draw_cell(j + 1, i + 1, color, bomb=is_bomb, only_create=not show_grid)
                else:
                    self.draw_cell(j + 1, i + 1, bomb=is_bomb, only_create=not show_grid)

        for row in self.cells:
            for cell in row:
                self.game.check_cell_env(cell.x_idx, cell.y_idx, False)

    def draw_string(self, string, _x, _y):
        font = pygame.font.SysFont("Comic Sans MS", 25)
        text = font.render(string, False, (0, 0, 0))
        self.screen.blit(text, (_x + 15, _y))
        pygame.display.update()

    def draw_time(self):
        tim = time.strftime("%M:%S")
        self.draw_string(tim, 0, 0)


class MineSweeper:
    def __init__(self, x_fields, y_fields, bombs, cells_size=40, screen=None):
        self.x_fields = x_fields
        self.y_fields = y_fields
        self.cap = "minesweeper"
        self.interface = PyGameInterface(self.cap, bombs, x_fields, y_fields, self, cells_size, screen)
        self.can_reset = False
        self.flags = 0
        self.start = time.time()
        self.bomb_count = bombs

    def check_cell_env(self, x_idx, y_idx, draw=True):
        xl = [x_idx - 1, x_idx, x_idx + 1]
        yl = [y_idx - 1, y_idx, y_idx + 1]
        _y = -1
        bombs = 0
        for _rows in self.interface.cells:
            _y += 1
            _x = -1
            for _cell in _rows:
                _x += 1
                if _y in yl and _x in xl:
                    if self.interface.cells[_y][_x].is_bomb:
                        bombs += 1

        if bombs == 0 and draw:
            _y = -1
            for _rows in self.interface.cells:
                _y += 1
                _x = -1
                for _cell in _rows:
                    _x += 1
                    if not _cell.is_bomb and _y in yl and _x in xl:
                        self.click_cell(_cell.x_idx, _cell.y_idx)

        if draw:
            self.interface.cells[y_idx][x_idx].draw(num=bombs)
            if bombs > 0:
                self.interface.cells[y_idx][x_idx].draw_number(bombs)
        else:
            self.interface.cells[y_idx][x_idx].neighbours = bombs
        return self.interface.cells[y_idx][x_idx]

    def show_bombs(self, won):
        for rows_ in self.interface.cells:
            for cell_ in rows_:
                if cell_.is_bomb:
                    if won:
                        cell_.draw(color=(255, 165, 0))
                    else:
                        cell_.draw(color=(126, 25, 27))

    def click_cell(self, _x, _y):
        _cell = self.interface.cells[_y][_x]

        if _cell.is_bomb:
            self.show_bombs(False)
            self.can_reset = True
            return None
        elif not _cell.looked_up:
            _cell.looked_up = True
            c = self.check_cell_env(_x, _y)
            return c
        if _cell.marked:
            _cell.marked = False
            self.flags -= 1
        return False

    def mark_cell(self, _cell, val=None):
        if val:
            _cell.marked = True
            _cell.draw(color=(77, 25, 77))
            self.flags += 1
            return _cell
        _marked = False
        _marked = False
        if _cell.marked:
            _cell.marked = False
            _cell.draw()
            self.flags -= 1
        elif self.flags < self.interface.bomb_count and not _cell.looked_up:
            _cell.draw(color=(77, 25, 77))
            _cell.marked = True
            self.flags += 1
            _marked = True
        return _cell

    def check_win(self):
        correct_cells = 0
        for rows_ in self.interface.cells:
            for cell_ in rows_:
                if cell_.is_bomb and cell_.marked:
                    correct_cells += 1
        if correct_cells == self.interface.bomb_count:
            self.show_bombs(True)
            val_d = ((((time.time() - self.start) / 365) / 24) / 60)
            days = int(val_d)

            val_h = (val_d - days) * 365
            hours = int(val_h)

            val_m = (val_h - hours) * 24
            minutes = int(val_m)

            val_s = (val_m - minutes) * 60
            seconds = int(val_s)
            self.interface.draw_string(f"{hours}:{minutes}:{seconds}", 30, 0)
            self.can_reset = True
            return True

    def start_game(self):
        self.interface.draw_field()
        left, right = 1, 3

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.can_reset:
                    if event.button == left:
                        for rows in self.interface.cells:
                            for cell in rows:
                                if cell.collidepoint(event.pos):
                                    self.click_cell(cell.x_idx, cell.y_idx)
                    elif event.button == right:
                        for rows in self.interface.cells:
                            for cell in rows:
                                if cell.collidepoint(event.pos):
                                    _rect: Cell = self.mark_cell(cell)
                                    self.interface.cells[cell.y_idx][cell.x_idx] = _rect
                    self.check_win()
                elif event.type == pygame.KEYDOWN:
                    if self.can_reset:
                        self.can_reset = False
                        pygame.quit()
                        self.interface = PyGameInterface(self.cap, self.bomb_count, self.x_fields, self.y_fields, self)
                        self.interface.draw_field()
                        self.flags = 0
                        self.start = time.time()


if __name__ == '__main__':
    fields_x, fields_y = 20, 10
    bombs = fields_x * fields_y // 5
    print(f"Bombs: {bombs}")
    minesweeper = MineSweeper(fields_x, fields_y, bombs)
    minesweeper.start_game()
