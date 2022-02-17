import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


"""
Each iteration:
Any live cell with fewer than two live neighbours dies, as if by underpopulation.
Any live cell with two or three live neighbours lives on to the next generation.
Any live cell with more than three live neighbours dies, as if by overpopulation.
Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
processed:
Any live cell with two or three live neighbours survives.
Any dead cell with three live neighbours becomes a live cell.
All other live cells die in the next generation. Similarly, all other dead cells stay dead.
"""


class Cell:
    def __init__(self, cord_x: int, cord_y: int, init_state=False):
        self.x = cord_x
        self.y = cord_y
        self.state = init_state

    def __add__(self, other):
        if type(other) == list:
            other[0].append(self.x)
            other[1].append(self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.state == other.state

    def __hash__(self):
        return hash((self.x, self.y, self.state))


class LifeCycle:
    def __init__(self, init_life: set):
        self.life = init_life
        self.dead_set = set()
        self.next_life_set = set()

        self.ydata = []
        self.xdata = []
        self.fig, self.ax = plt.subplots()
        self.ln, = plt.plot([], [], 'r+')

    def evaluate_life(self) -> None:
        for soul in self.life:
            neighbour_count = self.find_neighbours(soul)
            if neighbour_count in (2, 3):
                soul.state = True
                self.next_life_set.add(soul)

    def revive(self) -> None:
        for body in self.dead_set:
            neighbour_count = self.find_neighbours(body)
            if neighbour_count == 3:
                body.state = True
                self.next_life_set.add(body)

    def new_cycle(self) -> None:
        self.life = self.next_life_set
        self.next_life_set = set()
        self.dead_set = set()

    def run(self):
        self.evaluate_life()
        self.revive()
        self.new_cycle()

    def find_neighbours(self, node: Cell):
        neighbour_count = []
        neigh_coords = (-1, 0, 1)
        for y in neigh_coords:
            for x in neigh_coords:
                if (node.x + x == node.x) and (node.y + y == node.y):
                    pass
                else:
                    if Cell(node.x + x, node.y + y, True) in self.life:
                        neighbour_count.append(1)
                    elif node.state:
                        self.dead_set.add(Cell(node.x + x, node.y + y))
        return len(neighbour_count)

    def convert(self, node_lst):
        coords = [[], []]
        for nod in node_lst:
            nod + coords
        return coords

    def display(self):
        anim = animation.FuncAnimation(self.fig, self.update, init_func=self.init)
        plt.show()

    def init(self):
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        return self.ln,

    def update(self, frame):
        # time.sleep(1)
        self.run()
        new_iter = self.convert(self.life)
        self.xdata = new_iter[0]
        self.ydata = new_iter[1]
        self.ln.set_data(self.xdata, self.ydata)
        return self.ln,


if __name__ == '__main__':
    lives = set()

    live_object = (
        Cell(1, 1, True),
        Cell(2, 2, True),
        Cell(3, 2, True),
        Cell(1, 3, True),
        Cell(2, 3, True)
    )

    for cell in live_object:
        lives.add(cell)

    life_game = LifeCycle(lives)
    life_game.display()






