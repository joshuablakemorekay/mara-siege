"""
Automated checks for Mara's Siege - run with:  python -m unittest discover tests

The game runs headless here (no window, no sound), and each test drives the real
Game class the same way a player would: placing towers, starting waves and letting
time pass with game.update().
"""

import os
import sys
import unittest
from unittest import mock

os.environ["SDL_VIDEODRIVER"] = "dummy"  # No window
os.environ["SDL_AUDIODRIVER"] = "dummy"  # No sound
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
import config
pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
from main import Game

FRAME = 1 / 60


def tile_centre(grid_x, grid_y):
    """Pixel position of the middle of a grid tile"""
    return (grid_x * config.TILE_SIZE + config.TILE_SIZE // 2,
            grid_y * config.TILE_SIZE + config.TILE_SIZE // 2)


def run_for(game, seconds):
    for _ in range(int(seconds / FRAME)):
        game.update(FRAME)


def send_one_enemy(game, enemy_type, path=None):
    """Start a wave containing just one enemy, spawning on the next frame"""
    wm = game.wave_manager
    wm.current_wave = 1
    wm.start_next_wave()
    wm.enemies_to_spawn = [(enemy_type, path or game.paths[0])]
    wm.spawn_timer = wm.spawn_interval


class BuildRulesTest(unittest.TestCase):
    def test_garden_towers_go_on_grass_and_walls_on_paths(self):
        game = Game('normal', 'garden')
        game.resources.merit = 500
        game.selected_tower_type = 'viriya'
        game.try_place_tower(3, 7)  # (3, 7) is on the main road
        self.assertEqual(game.towers, [])
        game.try_place_tower(3, 6)  # Grass just above it
        self.assertEqual(len(game.towers), 1)

        game.build_mode = 'wall'
        game.try_place_wall(3, 5)  # Grass
        self.assertEqual(game.walls, [])
        game.try_place_wall(3, 7)  # Path
        self.assertEqual(len(game.walls), 1)

    def test_open_field_lets_you_build_anywhere(self):
        game = Game('normal', 'open')
        game.resources.merit = 500
        game.selected_tower_type = 'viriya'
        game.try_place_tower(3, 7)
        self.assertEqual(len(game.towers), 1)

    def test_cannot_build_on_any_temple_tile(self):
        game = Game('normal', 'garden')
        game.resources.merit = 500
        game.selected_tower_type = 'viriya'
        temple_x, temple_y = config.TEMPLE_POSITION
        game.try_place_tower(temple_x + 1, temple_y + 1)  # Bottom-right of the 2x2 temple
        self.assertEqual(game.towers, [])


class SellingTest(unittest.TestCase):
    def test_tower_refunds_half_of_build_and_upgrade_costs(self):
        game = Game('normal', 'garden')
        game.resources.merit, game.resources.concentration, game.resources.mindfulness = 500, 100, 100
        game.selected_tower_type = 'samadhi'
        game.try_place_tower(3, 3)
        game.selected_tower = game.towers[0]
        game.try_upgrade_selected()
        before = game.resources.get_resources()

        with mock.patch('pygame.mouse.get_pos', return_value=tile_centre(3, 3)):
            game.sell_structure_at_cursor()

        stats = config.TOWER_STATS['samadhi']
        after = game.resources.get_resources()
        self.assertEqual(game.towers, [])
        self.assertEqual(after['merit'] - before['merit'], (stats['cost_merit'] + stats['upgrade_cost_merit']) // 2)
        self.assertEqual(after['concentration'] - before['concentration'],
                         (stats['cost_concentration'] + stats['upgrade_cost_concentration']) // 2)


class WallLevelTest(unittest.TestCase):
    def wall_vs_enemy(self, level):
        """Put a wall of the given level on the main road and send one Doubt Mara at it"""
        game = Game('normal', 'garden')
        game.resources.merit, game.resources.concentration = 500, 500
        game.build_mode = 'wall'
        game.try_place_wall(4, 7)
        game.handle_left_click(tile_centre(4, 7))  # Select it
        for _ in range(level - 1):
            game.try_upgrade_selected()
        send_one_enemy(game, 'doubt')
        run_for(game, 6)
        return game.walls[0], game.wave_manager.enemies[0]

    def test_level_1_only_slows(self):
        wall, enemy = self.wall_vs_enemy(1)
        self.assertGreater(enemy.x, wall.x)  # Got past the wall
        self.assertEqual(enemy.health, enemy.max_health)  # No burn at level 1

    def test_level_2_slows_and_burns(self):
        wall, enemy = self.wall_vs_enemy(2)
        self.assertEqual(wall.level, 2)
        self.assertLess(enemy.health, enemy.max_health)

    def test_level_3_blocks_completely(self):
        wall, enemy = self.wall_vs_enemy(3)
        self.assertEqual(wall.level, 3)
        self.assertLess(enemy.x, wall.x)  # Still stuck on the near side
        self.assertEqual(enemy.speed, 0)


class EnemyPowerTest(unittest.TestCase):
    def test_envy_steals_merit_when_it_reaches_the_temple(self):
        game = Game('normal', 'garden')
        game.resources.merit = 100
        send_one_enemy(game, 'envy')
        for _ in range(int(40 / FRAME)):
            game.update(FRAME)
            if game.temple.breaches:
                break
        self.assertEqual(game.temple.breaches, 1)
        steal = config.ENEMY_STATS['envy']['merit_steal']
        self.assertEqual(game.resources.merit, 100 - steal)

    def test_anger_stuns_a_tower_beside_the_path(self):
        game = Game('normal', 'garden')
        game.resources.merit = 500
        game.selected_tower_type = 'viriya'
        game.try_place_tower(5, 6)
        tower = game.towers[0]
        send_one_enemy(game, 'anger')
        stunned = False
        for _ in range(int(10 / FRAME)):
            game.update(FRAME)
            stunned = stunned or tower.stunned_timer > 0
        self.assertTrue(stunned)


class DifficultyTest(unittest.TestCase):
    def test_each_difficulty_sets_waves_resources_and_final_boss(self):
        from difficulty import DIFFICULTIES
        for key, settings in DIFFICULTIES.items():
            with self.subTest(difficulty=key):
                game = Game(key, 'garden')
                self.assertEqual(game.wave_manager.total_waves, settings['waves'])
                self.assertEqual(game.resources.merit, settings['starting_merit'])
                self.assertEqual(game.wave_manager.boss_waves[settings['waves']], config.FINAL_BOSS)

    def test_harder_difficulty_makes_tougher_enemies(self):
        def first_enemy_health(difficulty):
            game = Game(difficulty, 'garden')
            send_one_enemy(game, 'doubt')
            game.update(FRAME)
            return game.wave_manager.enemies[0].max_health

        self.assertLess(first_enemy_health('easy'), first_enemy_health('extreme'))


class ScreenShakeTest(unittest.TestCase):
    def test_shake_moves_the_map_but_not_the_side_panel(self):
        game = Game('normal', 'garden')
        game.draw()
        panel = pygame.Rect(config.UI_PANEL_X, 0, config.UI_PANEL_WIDTH, config.SCREEN_HEIGHT)
        still_panel = game.screen.subsurface(panel).copy()

        game.screen_shake = 15
        game.draw()
        shaken_panel = game.screen.subsurface(panel).copy()
        self.assertEqual(pygame.image.tobytes(still_panel, 'RGB'), pygame.image.tobytes(shaken_panel, 'RGB'))

    def test_shake_fades_away(self):
        game = Game('normal', 'garden')
        game.screen_shake = 20
        run_for(game, 1)
        self.assertEqual(game.screen_shake, 0)


class FullGameTest(unittest.TestCase):
    def test_both_maps_play_ten_waves_without_crashing(self):
        for map_mode in ('garden', 'open'):
            with self.subTest(map=map_mode):
                game = Game('normal', map_mode)
                game.resources.merit, game.resources.concentration = 2000, 500
                for i, spot in enumerate([(3, 6), (6, 8), (8, 6), (11, 5), (8, 9), (11, 8)]):
                    game.selected_tower_type = ('sati', 'viriya', 'samadhi')[i % 3]
                    game.try_place_tower(*spot)
                # This checks for crashes, not winning - keep the temple standing so the run
                # reaches the wave 10 boss whatever happens
                game.temple.max_health = game.temple.health = 10 ** 6
                game.temple.max_breaches = 10 ** 6
                frame = 0
                while game.wave_manager.current_wave < 10 or game.wave_manager.wave_in_progress:
                    if not game.wave_manager.wave_in_progress:
                        game.wave_manager.start_next_wave()
                    game.update(1 / 30)
                    frame += 1
                    if frame % 10 == 0:
                        game.draw()
                self.assertEqual(game.state, config.STATE_PLAYING)
                self.assertEqual(game.wave_manager.current_wave, 10)


if __name__ == '__main__':
    unittest.main()
