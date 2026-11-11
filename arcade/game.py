"""Snake game state machine.

The arena product is small on purpose: the evaluation is about how the squad
delivers, not about the size of the game. This module is the stable core and
has no I/O so it stays easy to test.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


class GameError(ValueError):
    """Invalid move or state."""


@dataclass
class Game:
    width: int = 20
    height: int = 20
    seed: int = 1234
    body: list[tuple[int, int]] = field(default_factory=list)
    direction: str = "right"
    alive: bool = True
    score: int = 0
    food: tuple[int, int] | None = None
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.width < 5 or self.height < 5:
            raise GameError("board must be at least 5x5")
        self._rng = random.Random(self.seed)
        center = (self.width // 2, self.height // 2)
        self.body = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self._place_food()

    def turn(self, direction: str) -> None:
        if direction not in DIRECTIONS:
            raise GameError(f"unknown direction {direction!r}")
        if not self.alive:
            raise GameError("game over")
        if direction == OPPOSITE[self.direction]:
            raise GameError("cannot reverse into yourself")
        self.direction = direction

    def step(self) -> None:
        if not self.alive:
            raise GameError("game over")
        dx, dy = DIRECTIONS[self.direction]
        head = (self.body[0][0] + dx, self.body[0][1] + dy)

        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height):
            self.alive = False
            return
        if head == self.food:
            self.body.insert(0, head)
            self.score += 10
            self._place_food()
            return
        if head in self.body[:-1]:
            self.alive = False
            return
        self.body.insert(0, head)
        self.body.pop()

    def _place_food(self) -> None:
        free = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self.body
        ]
        self.food = self._rng.choice(free) if free else None
