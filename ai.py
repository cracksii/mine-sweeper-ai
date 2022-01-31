from pyGame.MineSweeper.mine_sweeper import *
from stuff.stuff import loop


class Rule:
    def __init__(self, mines=-1, fields=None):
        if fields is None:
            self.fields = set()
        else:
            self.fields = fields
        self.mines = mines

    def add(self, val):
        return self.fields.add(val)

    def remove(self, val):
        return self.fields.remove(val)

    def __repr__(self):
        return str(self.fields) + ", " + str(self.mines)


class AI(MineSweeper):
    def __init__(self, x_fields, y_fields, bombs, show_time=None, screen=None, cell_size=40, show_grid=False):
        super().__init__(x_fields, y_fields, bombs, cell_size, screen)
        self.unlocked = set()
        self.mines = set()
        self.rules = []
        self.screen = screen
        self.cell_size = cell_size
        self.show_grid = show_grid
        self.fields = [[] for _ in range(self.y_fields)]
        self.show_time = show_time
        self.preferred = [(x_fields - 1, y_fields - 1), (0, y_fields - 1), (x_fields - 1, 0)]
        for row in self.fields:
            for i in range(x_fields):
                row.append(None)
        self.interface.draw_field(show_grid=show_grid)
        self.last_rules = None
        self.rule_counter = 0

    def solve(self):
        did_not_change = -1
        unlocked = self.unlocked.copy()
        mines = self.mines.copy()

        while True:
            if self.unlocked == unlocked and self.mines == mines:
                did_not_change += 1
                c = self.check(0, 0)
                if c == "Error":
                    return False
            else:
                unlocked = self.unlocked.copy()
                mines = self.mines.copy()

            self.update_rules()
            if did_not_change >= 1:
                x, y = self.find_next_empty()
                val = self.check(x, y)
                if val == "Error":
                    return False
                did_not_change = 0
            if self.check_win():
                return True
            # time.sleep(0.25)

    def mark_as_bomb(self, x_idx, y_idx):
        self.mines.add((x_idx, y_idx))
        self.mark_cell(self.interface.cells[y_idx][x_idx], True)

    def check_neighbours(self, cell):
        xl = [cell.x_idx - 1, cell.x_idx, cell.x_idx + 1]
        yl = [cell.y_idx - 1, cell.y_idx, cell.y_idx + 1]
        _y = -1
        rule = Rule(cell.neighbours)
        for _rows in self.interface.cells:
            _y += 1
            _x = -1
            for _cell in _rows:
                _x += 1
                if _y in yl and _x in xl:
                    if _y != cell.y_idx or _x != cell.x_idx:
                        rule.add((_cell.x_idx, _cell.y_idx))
        self.rules.append(rule)

    def reveal_all_neighbours(self, cell):
        xl = [cell.x_idx - 1, cell.x_idx, cell.x_idx + 1]
        yl = [cell.y_idx - 1, cell.y_idx, cell.y_idx + 1]
        _y = -1
        for _rows in self.interface.cells:
            _y += 1
            _x = -1
            for _cell in _rows:
                _x += 1
                if _y in yl and _x in xl:
                    cell: Cell = self.click_cell(_x, _y)
                    if cell is None:
                        print(f"Field {_x, _y} was a bomb")
                    elif cell:
                        self.fields[cell.y_idx][cell.x_idx] = cell
                        self.unlocked.add((cell.x_idx, cell.y_idx))
                        self.check_neighbours(cell)

    def check(self, _x, _y):
        cell: Cell = self.click_cell(_x, _y)
        if cell:
            self.unlocked.add((cell.x_idx, cell.y_idx))
            self.fields[cell.y_idx][cell.x_idx] = cell
            self.check_neighbours(cell)
            return cell
        elif cell is None:
            return "Error"

    def find_next_empty(self):
        x, y = -1, 0
        while True:
            if self.preferred:
                val = self.preferred[0]
                self.preferred.remove(val)
                if (val[0], val[1]) not in self.mines and (val[0], val[1]) not in self.unlocked:
                    return val[0], val[1]
            x = x + 1
            if x >= self.x_fields:
                y = y + 1 if y <= self.y_fields else 0
                x = 0
            if (x, y) not in self.mines and (x, y) not in self.unlocked:
                return x, y

    def update_rules(self):
        if self.last_rules != self.rules:
            self.rule_counter = 0
        else:
            self.rule_counter += 1
        if self.rule_counter > 5:
            print("Error")
            exit()
        for revealed in self.unlocked:
            for rule in self.rules:
                if revealed in rule.fields:
                    rule.fields.remove(revealed)

        for rule in self.rules:
            if len(rule.fields) == rule.mines:
                for field in rule.fields:
                    self.mark_as_bomb(field[0], field[1])
                    self.mines.add((field[0], field[1]))
            elif rule.mines == 0:
                for field in rule.fields:
                    self.check(field[0], field[1])
                    self.unlocked.add((field[0], field[1]))
                self.rules.remove(rule)

        for rule in self.rules:
            for sub_rule in self.rules:
                if sub_rule.fields is not rule.fields:
                    # print(sub_rule.fields, sub_rule.mines, " " * 50, rule.fields, rule.mines)
                    pass
                if sub_rule.fields.issubset(rule.fields) and sub_rule.fields is not rule.fields:
                    rule.fields -= sub_rule.fields
                    rule.mines -= sub_rule.mines
                    # print("Res:", rule.fields, rule.mines)
        # print("\n")
        new_rules = []
        for rule in self.rules:
            new_rule = Rule()
            mines = rule.mines
            for field in rule.fields:
                if field in self.unlocked:
                    pass
                elif field in self.mines:
                    mines -= 1
                else:
                    new_rule.add(field)
            new_rule.mines = mines
            if len(new_rule.fields) > 0:
                new_rules.append(new_rule)

        self.rules = new_rules

    def show_bombs(self, won=False):
        for rows_ in self.interface.cells:
            for cell_ in rows_:
                if cell_.is_bomb:
                    if won:
                        cell_.draw(color=(255, 165, 0))
                    else:
                        cell_.draw(color=(126, 25, 27))
                    if self.show_time:
                        time.sleep(self.show_time)

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
        if draw:
            self.interface.cells[y_idx][x_idx].draw(num=bombs)
            if bombs > 0:
                self.interface.cells[y_idx][x_idx].draw_number(bombs)
        else:
            self.interface.cells[y_idx][x_idx].neighbours = bombs
        return self.interface.cells[y_idx][x_idx]

    def reset(self):
        self.interface.draw_screen((100, 100, 100))
        self.interface.__init__(self.cap, self.bomb_count, self.x_fields, self.y_fields, self, self.cell_size,
                                self.screen)
        self.flags = 0
        self.start = time.time()
        self.unlocked = set()
        self.mines = set()
        self.rules = []
        self.fields = [[] for _ in range(self.y_fields)]
        self.preferred = [(self.x_fields - 1, self.y_fields - 1), (0, self.y_fields - 1), (self.x_fields - 1, 0)]
        for row in self.fields:
            for i in range(self.x_fields):
                row.append(None)
        self.interface.draw_field(show_grid=self.show_grid)
        self.last_rules = None
        self.rule_counter = 0


def benchmark(_x, _y, divisor=10, cz=40, screen=None, runs=100):
    x = {"runs": runs, "wins": 0}
    val1, val2 = _x, _y
    if screen == "full":
        screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)

    @loop(x["runs"])
    def inner(r):
        ai = AI(val1, val2, val1 * val2 // divisor, cell_size=cz, show_grid=False, screen=screen, show_time=0)
        x["runs"] = r
        if ai.solve():
            x["wins"] += 1
            # print(f"Solved {val1} x {val1} ({val1 * val2 // divisor} bombs)")

    print(x["wins"], x["runs"], x["wins"] / x["runs"])


def illustrate():
    sizes = [(3, 3), (7, 7), (10, 10), (15, 15), (20, 20), (45, 24)]
    idx = 0
    while True:
        try:
            ai = AI(sizes[idx][0], sizes[idx][1], sizes[idx][0] * sizes[idx][1] // 7, show_time=0.05)
        except IndexError:
            return
        if ai.solve():
            idx += 1
        time.sleep(3)


benchmark(45, 24, divisor=10, cz=40, runs=100, screen="full")  # <- Fullscreen
# benchmark(86, 24, cz=40)  # <- greatest field 40px
# benchmark(90, 50, cz=20)  # <- greatest field 20px
# benchmark(225, 95, cz=7)  # <- greatest field 20px
# illustrate()
