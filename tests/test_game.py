import unittest

from arcade.game import Game, GameError


class GameTests(unittest.TestCase):
    def test_starts_with_three_segments(self):
        game = Game()
        self.assertEqual(len(game.body), 3)
        self.assertTrue(game.alive)
        self.assertEqual(game.score, 0)
        self.assertIsNotNone(game.food)

    def test_step_moves_the_head(self):
        game = Game()
        tail = game.body[-1]
        game.step()
        self.assertEqual(game.body[0], (11, 10))
        self.assertNotIn(tail, game.body)

    def test_eating_grows_and_scores(self):
        game = Game()
        game.food = (11, 10)
        game.step()
        self.assertEqual(game.score, 10)
        self.assertEqual(len(game.body), 4)

    def test_reverse_is_rejected(self):
        game = Game()
        with self.assertRaises(GameError):
            game.turn("left")

    def test_wall_collision_ends_the_game(self):
        game = Game(width=5, height=5)
        game.body = [(4, 2), (3, 2), (2, 2)]
        game.direction = "right"
        game.step()
        self.assertFalse(game.alive)
        with self.assertRaises(GameError):
            game.step()

    def test_self_collision_ends_the_game(self):
        game = Game()
        game.body = [(2, 2), (2, 3), (3, 3), (3, 2), (4, 2)]
        game.direction = "down"
        game.body = [(2, 2), (1, 2), (1, 3), (2, 3), (3, 3)]
        game.step()
        self.assertFalse(game.alive)

    def test_seed_is_reproducible(self):
        a, b = Game(seed=7), Game(seed=7)
        self.assertEqual(a.food, b.food)

    def test_board_must_not_be_tiny(self):
        with self.assertRaises(GameError):
            Game(width=4, height=4)


if __name__ == "__main__":
    unittest.main()
