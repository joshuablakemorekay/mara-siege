"""
Mara's Siege - Main Game File
A Buddhist-themed tower defense game
"""

import pygame
import sys
import math
import random
from config import *
from resource_manager import ResourceManager
from temple import Temple
from tower import SatiTower, ViriyaTower, SamadhiTower
from wave_manager import WaveManager
from particles import ParticleSystem
from wall import Wall
from main_menu import MainMenu
from floating_text import FloatingTextManager
from abilities import AbilityManager
import sounds
from terrain import render_terrain, build_path_tiles


class Game:
    """Main game class"""
    
    def __init__(self, difficulty='normal', map_mode=DEFAULT_MAP_MODE):
        # Get existing display (already initialized by main())
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Mara's Siege - Defend the Temple")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load difficulty settings
        from difficulty import DIFFICULTIES
        self.difficulty = DIFFICULTIES[difficulty]
        self.difficulty_key = difficulty
        
        # Game state
        self.state = STATE_PLAYING
        
        # Map - Temple Garden has paths and terraces, Open Field is free roaming
        self.map_mode = map_mode
        if map_mode == 'garden':
            self.paths = PATHS
            self.path_tiles = build_path_tiles(PATHS)
            self.terrain = render_terrain(self.paths, self.path_tiles)  # Drawn once, reused every frame
        else:
            self.paths = [[spawn] for spawn in OPEN_FIELD_SPAWNS]  # Straight line to the temple
            self.path_tiles = set()
            self.terrain = None

        # Core systems
        self.resources = ResourceManager()
        self.resources.merit = self.difficulty['starting_merit']
        self.resources.concentration = self.difficulty['starting_concentration']
        self.resources.mindfulness = self.difficulty['starting_mindfulness']
        self.temple = Temple()
        self.wave_manager = WaveManager(self.temple.get_center(), self.paths, self.difficulty)
        self.particle_system = ParticleSystem()
        self.floating_text = FloatingTextManager()  # NEW! Damage numbers
        self.abilities = AbilityManager()  # NEW! Special abilities
        
        # Towers
        self.towers = []
        self.selected_tower = None  # For upgrading
        self.selected_wall = None  # Walls can be upgraded too
        
        # Walls - NEW!
        self.walls = []
        
        # UI state
        self.selected_tower_type = 'viriya'  # Default - cheapest tower!
        self.build_mode = 'tower'  # NEW! 'tower' or 'wall'
        self.hovered_tile = None
        self.show_perfect_wave_message = False
        self.perfect_wave_timer = 0
        self.feedback_message = ""
        self.feedback_color = (255, 255, 255)
        self.feedback_timer = 0
        
        # Slow motion state - NEW!
        self.slow_motion_active = False
        self.slow_motion_timer = 0
        self.slow_motion_factor = 0.2  # 20% speed (80% slower!)
        self.screen_shake = 0  # Camera shake intensity
        self.flash_alpha = 0  # White flash effect
        self.announced_boss_wave = 0  # Last boss wave we showed a warning for
        self.bell_rung_for_wave = 0  # Last wave we rang the start bell for

        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_left_click(event.pos)
                elif event.button == 3:  # Right click - upgrade selected tower or wall
                    self.try_upgrade_selected()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Manual wave start (for testing)
                    if not self.wave_manager.wave_in_progress:
                        self.wave_manager.start_next_wave()
                # Tower selection hotkeys
                elif event.key == pygame.K_1:
                    self.selected_tower_type = 'sati'
                    self.build_mode = 'tower'
                elif event.key == pygame.K_2:
                    self.selected_tower_type = 'viriya'
                    self.build_mode = 'tower'
                elif event.key == pygame.K_3:
                    self.selected_tower_type = 'samadhi'
                    self.build_mode = 'tower'
                # Wall mode hotkey
                elif event.key == pygame.K_w:
                    if self.build_mode == 'wall':
                        self.build_mode = 'tower'
                        self.show_message("Tower mode", (100, 200, 255))
                    else:
                        self.build_mode = 'wall'
                        self.show_message("Wall mode", (120, 100, 80))
                # Clear cursor (ESC or X)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                    self.selected_tower_type = None
                    self.selected_tower = None
                    self.selected_wall = None
                    self.build_mode = None
                    self.show_message("Cursor cleared - Press 1/2/3 or W to build", (200, 200, 200))
                # Sell tower/wall under the cursor
                elif event.key == pygame.K_s:
                    self.sell_structure_at_cursor()
                # Mute / unmute sound
                elif event.key == pygame.K_m:
                    muted = sounds.toggle_mute()
                    self.show_message("Sound off" if muted else "Sound on", (200, 200, 200))

    def handle_left_click(self, pos):
        """Handle left clicks - select tower or place tower/wall or use ability"""
        mouse_x, mouse_y = pos
        
        # Check if click is on ability objects FIRST
        if self.check_ability_click(mouse_x, mouse_y):
            return  # Ability was triggered
        
        # Check if click is on grid
        if mouse_x < GRID_WIDTH and mouse_y < GRID_HEIGHT:
            grid_x = mouse_x // TILE_SIZE
            grid_y = mouse_y // TILE_SIZE
            
            # Try to select existing tower first (only in tower mode)
            if self.build_mode == 'tower':
                for tower in self.towers:
                    # Larger click hitbox for easier selection
                    click_padding = 10  # Extra pixels around tower
                    tower_rect = pygame.Rect(
                        tower.x - tower.size // 2 - click_padding,
                        tower.y - tower.size // 2 - click_padding,
                        tower.size + click_padding * 2,
                        tower.size + click_padding * 2
                    )
                    if tower_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_tower = tower
                        self.selected_wall = None
                        self.show_message(f"{tower.name} selected - Right-click to upgrade", (255, 215, 0))
                        return

            # Clicking an existing wall selects it (in either build mode)
            for wall in self.walls:
                if wall.grid_x == grid_x and wall.grid_y == grid_y:
                    self.selected_wall = wall
                    self.selected_tower = None
                    self.show_message(f"Wall (Level {wall.level}) selected - Right-click to upgrade", (255, 215, 0))
                    return

            # Nothing clicked, try to place tower or wall
            self.selected_wall = None
            if self.build_mode == 'tower':
                self.try_place_tower(grid_x, grid_y)
                self.selected_tower = None  # Deselect after placing
            else:  # wall mode
                self.try_place_wall(grid_x, grid_y)
        
        # Check UI button clicks
        elif mouse_x >= UI_PANEL_X:
            self.handle_ui_click(pos)
    
    def try_upgrade_wall(self):
        """Attempt to upgrade the selected wall (right-click)"""
        wall = self.selected_wall
        if not wall.can_upgrade():
            self.show_message("Wall already at MAX level!", (255, 150, 50))
            return

        cost_merit, cost_concentration = wall.get_upgrade_cost()
        if self.resources.can_afford(merit=cost_merit, concentration=cost_concentration):
            self.resources.spend(merit=cost_merit, concentration=cost_concentration)
            wall.upgrade()
            self.show_message(f"Wall upgraded to Level {wall.level}! {wall.stats['effect']}", (100, 255, 100))
            sounds.play('upgrade')
        else:
            self.show_message("Not enough resources to upgrade!", (255, 100, 100))
            sounds.play('error')

    def try_upgrade_selected(self):
        """Attempt to upgrade the selected tower or wall (right-click)"""
        if self.selected_wall:
            self.try_upgrade_wall()
            return
        if not self.selected_tower:
            self.show_message("Nothing selected - click a tower or wall first", (255, 150, 50))
            return
            
        if not self.selected_tower.can_upgrade():
            self.show_message("Tower already at MAX level!", (255, 150, 50))
            return
        
        upgrade_info = self.selected_tower.get_upgrade_info()
        
        # Check if can afford
        can_afford = self.resources.can_afford(
            merit=upgrade_info['cost_merit'],
            concentration=upgrade_info['cost_concentration'],
            mindfulness=upgrade_info['cost_mindfulness']
        )
        
        if can_afford:
            # Spend resources
            self.resources.spend(
                merit=upgrade_info['cost_merit'],
                concentration=upgrade_info['cost_concentration'],
                mindfulness=upgrade_info['cost_mindfulness']
            )
            # Upgrade tower
            self.selected_tower.upgrade()
            self.show_message(f"Tower upgraded to Level {self.selected_tower.level}!", (100, 255, 100))
            sounds.play('upgrade')
        else:
            self.show_message("Not enough resources to upgrade!", (255, 100, 100))
            sounds.play('error')
    
    def sell_structure_at_cursor(self):
        """Sell the tower or wall under the mouse for a 50% refund"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x >= GRID_WIDTH or mouse_y >= GRID_HEIGHT:
            self.show_message("Hover over a tower or wall to sell", (255, 150, 50))
            return
        grid_x = mouse_x // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE

        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                # Refund half of build cost plus half of every upgrade paid for
                stats = TOWER_STATS[tower.type]
                upgrades = tower.level - 1
                merit = (stats['cost_merit'] + stats['upgrade_cost_merit'] * upgrades) // 2
                concentration = (stats['cost_concentration'] + stats['upgrade_cost_concentration'] * upgrades) // 2
                mindfulness = (stats['cost_mindfulness'] + stats['upgrade_cost_mindfulness'] * upgrades) // 2
                self.resources.add_merit(merit)
                self.resources.add_concentration(concentration)
                self.resources.mindfulness += mindfulness
                self.towers.remove(tower)
                if self.selected_tower == tower:
                    self.selected_tower = None
                self.show_message(f"Tower sold! +{merit}M +{concentration}C +{mindfulness}F", (100, 255, 100))
                sounds.play('sell')
                return

        for wall in self.walls:
            if wall.grid_x == grid_x and wall.grid_y == grid_y:
                spent_merit, spent_concentration = wall.total_spent()
                merit = spent_merit // 2
                concentration = spent_concentration // 2
                self.resources.add_merit(merit)
                self.resources.add_concentration(concentration)
                self.walls.remove(wall)
                if self.selected_wall == wall:
                    self.selected_wall = None
                self.show_message(f"Wall sold! +{merit}M +{concentration}C", (100, 255, 100))
                sounds.play('sell')
                return

        self.show_message("Nothing to sell here", (255, 150, 50))

    def try_place_tower(self, grid_x, grid_y):
        """Try to place a tower at grid position"""
        # Don't place if cursor cleared
        if self.build_mode != 'tower' or self.selected_tower_type is None:
            return
        
        # Check if position is valid
        if not self.is_valid_build_position(grid_x, grid_y):
            # Show feedback - position invalid
            if self.is_path(grid_x, grid_y):
                self.show_message("Towers go on the grass, not the path!", (255, 100, 100))
                sounds.play('error')
            else:
                self.show_message("Invalid position!", (255, 100, 100))
                sounds.play('error')
            return
        
        # Get tower costs
        stats = TOWER_STATS[self.selected_tower_type]
        tower_cost_merit = stats['cost_merit']
        tower_cost_concentration = stats['cost_concentration']
        tower_cost_mindfulness = stats['cost_mindfulness']
        
        # Check if can afford
        if not self.resources.can_afford(
            merit=tower_cost_merit,
            concentration=tower_cost_concentration,
            mindfulness=tower_cost_mindfulness
        ):
            # Show feedback - can't afford
            self.show_message("Not enough resources!", (255, 150, 50))
            sounds.play('error')
            return
        
        # Spend resources and build tower
        self.resources.spend(
            merit=tower_cost_merit,
            concentration=tower_cost_concentration,
            mindfulness=tower_cost_mindfulness
        )
        
        # Create appropriate tower type
        if self.selected_tower_type == 'sati':
            tower = SatiTower(grid_x, grid_y)
        elif self.selected_tower_type == 'viriya':
            tower = ViriyaTower(grid_x, grid_y)
        elif self.selected_tower_type == 'samadhi':
            tower = SamadhiTower(grid_x, grid_y)
        
        self.towers.append(tower)
        # Show feedback - success!
        self.show_message("Tower placed!", (100, 255, 100))
        sounds.play('place')
    
    def try_place_wall(self, grid_x, grid_y):
        """Try to place a wall at grid position"""
        # Check if position is valid for walls
        if not self.is_valid_build_position(grid_x, grid_y):
            if self.map_mode == 'garden' and not self.is_path(grid_x, grid_y):
                self.show_message("Walls go on the path!", (255, 100, 100))
                sounds.play('error')
            else:
                self.show_message("Invalid position!", (255, 100, 100))
                sounds.play('error')
            return
        
        # Check if can afford wall
        if not self.resources.can_afford(
            merit=WALL_COST_MERIT,
            concentration=WALL_COST_CONCENTRATION
        ):
            self.show_message("Not enough resources!", (255, 150, 50))
            sounds.play('error')
            return
        
        # Spend resources and build wall
        self.resources.spend(
            merit=WALL_COST_MERIT,
            concentration=WALL_COST_CONCENTRATION
        )
        
        # Create wall
        wall = Wall(grid_x, grid_y, self.difficulty['wall_health_mult'])
        self.walls.append(wall)
        self.show_message("Wall placed!", (120, 100, 80))
        sounds.play('place')
    
    def update_wall_collisions(self, delta_time):
        """Check for enemy-wall collisions and apply damage"""
        for enemy in self.wave_manager.enemies:
            # Check collision with each wall
            for wall in self.walls[:]:
                if not wall.alive:
                    continue
                
                # Check distance
                dx = enemy.x - wall.x
                dy = enemy.y - wall.y
                distance = (dx**2 + dy**2)**0.5
                
                # If enemy is touching wall
                if distance < (TILE_SIZE // 2 + 10):
                    # Enemy attacks wall (bosses hit much harder)
                    attack = WALL_BOSS_ATTACK_DAMAGE if enemy.is_boss else WALL_ATTACK_DAMAGE
                    if wall.take_damage(attack * delta_time):
                        # Wall destroyed
                        self.walls.remove(wall)
                        if self.selected_wall == wall:
                            self.selected_wall = None
                        self.show_message("Wall destroyed!", (200, 100, 50))

                    # Wall slows the enemy (level 3 stops it dead) and burns it from level 2
                    enemy.speed = enemy.base_speed * wall.stats['speed']
                    if wall.stats['damage'] > 0:
                        enemy.take_damage(wall.stats['damage'] * delta_time)
                    break
            else:
                # No wall collision, full speed
                enemy.speed = enemy.base_speed
    
    def show_message(self, text, color):
        """Show a temporary feedback message"""
        self.feedback_message = text
        self.feedback_color = color
        self.feedback_timer = 2.0  # Show for 2 seconds
    
    def trigger_slow_motion(self, duration):
        """Trigger slow motion effect with WHITE FLASH"""
        self.slow_motion_active = True
        self.slow_motion_timer = duration
        self.screen_shake = 15  # Increased from 10! More shake!
        self.slow_motion_factor = 0.2  # Even slower! Was 0.3, now 0.2 (80% slower!)
        self.flash_alpha = 255  # Full white flash!
    
    def check_ability_click(self, mouse_x, mouse_y):
        """Check if ability object was clicked"""
        # Lotus Pond (Metta Healing)
        lotus_x = LOTUS_POND_POS[0] * TILE_SIZE + TILE_SIZE // 2
        lotus_y = LOTUS_POND_POS[1] * TILE_SIZE + TILE_SIZE // 2
        if self.point_in_circle(mouse_x, mouse_y, lotus_x, lotus_y, ABILITY_OBJECT_SIZE // 2):
            return self.use_ability('metta', self.resources, self)
        
        # Buddha Statue (Samadhi Wave)
        buddha_x = BUDDHA_STATUE_POS[0] * TILE_SIZE + TILE_SIZE // 2
        buddha_y = BUDDHA_STATUE_POS[1] * TILE_SIZE + TILE_SIZE // 2
        if self.point_in_circle(mouse_x, mouse_y, buddha_x, buddha_y, ABILITY_OBJECT_SIZE // 2):
            return self.use_ability('samadhi', self.resources, self)
        
        # Monk (Karuna Strike)
        monk_x = MONK_POS[0] * TILE_SIZE + TILE_SIZE // 2
        monk_y = MONK_POS[1] * TILE_SIZE + TILE_SIZE // 2
        if self.point_in_circle(mouse_x, mouse_y, monk_x, monk_y, ABILITY_OBJECT_SIZE // 2):
            return self.use_ability('karuna', self.resources, self)
        
        return False
    
    def use_ability(self, key, resources, game):
        """Use an ability, with a singing bowl tone if it worked"""
        used = self.abilities.use_ability(key, resources, game)
        if used:
            sounds.play('bowl')
        return used

    def is_path(self, grid_x, grid_y):
        """True if this tile is part of an enemy path (never, in Open Field)"""
        return (grid_x, grid_y) in self.path_tiles

    def point_in_circle(self, px, py, cx, cy, radius):
        """Check if point is in circle"""
        dx = px - cx
        dy = py - cy
        return (dx**2 + dy**2) <= radius**2
    
    def is_valid_build_position(self, grid_x, grid_y):
        """Check if can build at position"""
        # Check grid bounds
        if grid_x < 0 or grid_x >= GRID_COLS or grid_y < 0 or grid_y >= GRID_ROWS:
            return False
        
        # Check if temple location (the temple covers a 2x2 block of tiles)
        temple_tiles = TEMPLE_SIZE // TILE_SIZE
        if (TEMPLE_POSITION[0] <= grid_x < TEMPLE_POSITION[0] + temple_tiles and
                TEMPLE_POSITION[1] <= grid_y < TEMPLE_POSITION[1] + temple_tiles):
            return False

        # Temple Garden: towers go on the grass terraces, walls go on the paths
        if self.map_mode != 'garden':
            pass
        elif self.build_mode == 'wall':
            if not self.is_path(grid_x, grid_y):
                return False
        elif self.is_path(grid_x, grid_y):
            return False
        
        # Check if another tower exists
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return False
        
        # Check if a wall exists
        for wall in self.walls:
            if wall.grid_x == grid_x and wall.grid_y == grid_y:
                return False
        
        return True
    
    def handle_ui_click(self, pos):
        """Handle clicks on UI panel"""
        mouse_x, mouse_y = pos
        
        # Only handle tower selection if in tower mode
        if self.build_mode != 'tower':
            return
        
        # Tower selection buttons - MUST match draw_ui exactly!
        # In draw_ui: y_pos = 215, button_y = y_pos + 35 = 250
        button_start_y = 250  # CORRECTED from 290!
        button_height = 60
        button_spacing = 70
        button_left = UI_PANEL_X + 10
        button_right = SCREEN_WIDTH - 10
        
        # Check if click is within button area horizontally
        if button_left < mouse_x < button_right:
            # Check each button vertically
            # Button 1 (Sati): 250 to 310
            if button_start_y <= mouse_y <= button_start_y + button_height:
                self.selected_tower_type = 'sati'
                self.selected_tower = None
                self.build_mode = 'tower'
                self.show_message("Sati Tower selected", (100, 200, 255))
                return
            
            # Button 2 (Viriya): 320 to 380
            elif button_start_y + button_spacing <= mouse_y <= button_start_y + button_spacing + button_height:
                self.selected_tower_type = 'viriya'
                self.selected_tower = None
                self.build_mode = 'tower'
                self.show_message("Viriya Tower selected", (255, 150, 50))
                return
            
            # Button 3 (Samadhi): 390 to 450
            elif button_start_y + button_spacing * 2 <= mouse_y <= button_start_y + button_spacing * 2 + button_height:
                self.selected_tower_type = 'samadhi'
                self.selected_tower = None
                self.build_mode = 'tower'
                self.show_message("Samadhi Tower selected", (150, 100, 255))
                return
    
    def update(self, delta_time):
        """Update game state"""
        if self.state != STATE_PLAYING:
            return
        
        # Handle slow motion
        if self.slow_motion_active:
            self.slow_motion_timer -= delta_time
            if self.slow_motion_timer <= 0:
                self.slow_motion_active = False
            # Apply slow motion to delta time
            delta_time *= self.slow_motion_factor

        # Screen shake fades out every frame (it used to only fade during slow motion)
        self.screen_shake *= 0.9
        if self.screen_shake < 0.5:
            self.screen_shake = 0

        # Fade white flash
        if self.flash_alpha > 0:
            self.flash_alpha -= 15  # Fade speed
            if self.flash_alpha < 0:
                self.flash_alpha = 0
        
        # Regenerate mindfulness
        self.resources.regenerate_mindfulness(delta_time)
        
        # Update perfect wave message timer
        if self.show_perfect_wave_message:
            self.perfect_wave_timer -= delta_time
            if self.perfect_wave_timer <= 0:
                self.show_perfect_wave_message = False
        
        # Update feedback message timer
        if self.feedback_timer > 0:
            self.feedback_timer -= delta_time
        
        # Update wave manager
        self.wave_manager.update(delta_time)

        # Ring the temple bell when a wave begins (boss waves get a gong instead)
        wave = self.wave_manager.current_wave
        if self.wave_manager.wave_in_progress and self.bell_rung_for_wave != wave:
            self.bell_rung_for_wave = wave
            if wave not in self.wave_manager.boss_waves:
                sounds.play('bell')

        # Warn the player once when a boss wave begins
        if self.wave_manager.wave_in_progress and wave in self.wave_manager.boss_waves and self.announced_boss_wave != wave:
            self.announced_boss_wave = wave
            boss_name = ENEMY_STATS[self.wave_manager.boss_waves[wave]]['name']
            self.show_message(f"BOSS WAVE! {boss_name} approaches!", (255, 60, 60))
            sounds.play('gong')
            self.screen_shake = 10  # A rumble as the boss arrives
            self.feedback_timer = 4.0
        
        # Check wall collisions and damage
        self.update_wall_collisions(delta_time)
        
        # Check for wave completion and award bonuses
        if self.wave_manager.wave_complete and not self.wave_manager.wave_in_progress:
            # Only award once per wave
            if not hasattr(self, 'last_completed_wave'):
                self.last_completed_wave = 0
            
            if self.wave_manager.current_wave > self.last_completed_wave:
                was_perfect = self.wave_manager.was_perfect_wave()
                self.resources.wave_completion_bonus(
                    self.wave_manager.current_wave,
                    not was_perfect
                )
                self.last_completed_wave = self.wave_manager.current_wave
                
                # Visual feedback for perfect wave
                if was_perfect:
                    self.show_perfect_wave_message = True
                    self.perfect_wave_timer = 3.0  # Show for 3 seconds
        
        # Update particle system
        self.particle_system.update(delta_time)
        
        # Update floating text
        self.floating_text.update(delta_time)
        
        # Check for newly dead enemies and create death effects
        enemies = self.wave_manager.get_active_enemies()
        for enemy in self.wave_manager.enemies:
            if not enemy.alive and enemy.health <= 0:
                # Create death explosion
                self.particle_system.create_death_explosion(
                    enemy.x, enemy.y, enemy.color
                )
        
        # Update towers
        for tower in self.towers:
            tower.update(delta_time, enemies)
            
            # Anger Mara stuns the first tower it passes (once each)
            for enemy in enemies:
                if enemy.stuns_towers and not enemy.has_damaged_tower:
                    if enemy.distance_to(tower.x, tower.y) < ANGER_STUN_REACH:
                        enemy.has_damaged_tower = True
                        tower.stun(TOWER_STUN_TIME)
                        self.particle_system.create_death_explosion(tower.x, tower.y, (255, 150, 0))
                        self.floating_text.add_text(tower.x, tower.y - 25, "STUNNED", (255, 120, 60), size=20)
        
        # Check for dead enemies and show floating rewards BEFORE removing them
        for enemy in self.wave_manager.enemies:
            if not enemy.alive and not enemy.reached_temple:
                # Show floating reward text
                self.floating_text.add_merit_gain(enemy.x, enemy.y - 20, enemy.merit_reward)
                sounds.play('pop')
                if hasattr(enemy, 'concentration_reward') and enemy.concentration_reward > 0:
                    self.floating_text.add_concentration_gain(enemy.x, enemy.y, enemy.concentration_reward)
        
        # Remove dead enemies and collect resources
        merit_gained, concentration_gained = self.wave_manager.remove_dead_enemies()
        if merit_gained > 0:
            self.resources.add_merit(merit_gained)
        if concentration_gained > 0:
            self.resources.add_concentration(concentration_gained)
        
        # Check for temple breaches
        breaches = self.wave_manager.check_temple_breaches()
        for enemy in breaches:
            self.temple.register_breach(enemy.temple_damage)
            sounds.play('breach')
            if enemy.is_boss:
                self.screen_shake = 20  # A boss hitting the temple shakes the whole map
            
            # Envy Mara steals Merit when it gets through
            if enemy.merit_steal > 0:
                merit_stolen = min(enemy.merit_steal, self.resources.merit)
                self.resources.merit -= merit_stolen
                self.floating_text.add_text(self.temple.x + self.temple.size // 2, self.temple.y - 40,
                                            f"-{merit_stolen}M STOLEN", (255, 215, 0), size=24)
        
        # Check victory/defeat conditions
        if self.temple.is_destroyed() or self.temple.meditation_broken():
            self.state = STATE_DEFEAT
            sounds.play('defeat')
        elif self.wave_manager.is_victory() and self.resources.merit >= 1000:
            self.state = STATE_VICTORY
            sounds.play('victory')
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BACKGROUND)
        
        if self.state == STATE_PLAYING:
            self.draw_game()
            if self.screen_shake > 0:
                self.apply_screen_shake()
        elif self.state == STATE_VICTORY:
            self.draw_victory_screen()
        elif self.state == STATE_DEFEAT:
            self.draw_defeat_screen()
        
        pygame.display.flip()
    
    def apply_screen_shake(self):
        """Jolt the map by a random offset - the side panel stays still so it's readable"""
        strength = int(self.screen_shake)
        offset = (random.randint(-strength, strength), random.randint(-strength, strength))
        map_area = pygame.Rect(0, 0, GRID_WIDTH, GRID_HEIGHT)
        snapshot = self.screen.subsurface(map_area).copy()
        self.screen.set_clip(map_area)  # Don't let the shifted map spill over the side panel
        self.screen.fill(BACKGROUND, map_area)
        self.screen.blit(snapshot, offset)
        self.screen.set_clip(None)

    def draw_game(self):
        """Draw the main game"""
        # Draw the terrain (paths, terraces, cliffs) or the open field grid
        if self.terrain:
            self.screen.blit(self.terrain, (0, 0))
        else:
            self.draw_grid()
        self.draw_garden_decorations()
        
        # Draw temple
        self.temple.draw(self.screen)
        
        # Draw ability objects
        self.draw_ability_objects()
        
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw walls
        for wall in self.walls:
            wall.draw(self.screen)
        
        # Draw enemies
        for enemy in self.wave_manager.enemies:
            enemy.draw(self.screen)
            if enemy.is_boss and enemy.alive:
                self.draw_boss_health_bar(enemy)

        # Draw particle effects (death explosions)
        self.particle_system.draw(self.screen)
        
        # Draw floating text (damage numbers, rewards)
        self.floating_text.draw(self.screen)
        
        # Draw selected tower highlight
        if self.selected_tower or self.selected_wall:
            self.draw_selected_tower_highlight()
        
        # Draw UI panel
        self.draw_ui()
        
        # Draw hover preview
        self.draw_tower_preview()
        
        # Draw perfect wave message
        if self.show_perfect_wave_message:
            self.draw_perfect_wave_message()
        
        # Draw feedback messages
        if self.feedback_timer > 0:
            self.draw_feedback_message()
        
        # Draw white flash overlay (ability activation)
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.set_alpha(self.flash_alpha)
            flash_surface.fill((255, 255, 255))
            self.screen.blit(flash_surface, (0, 0))
    
    def draw_garden_decorations(self):
        """Draw meditation garden theme elements"""
        # Lotus pond (bottom left corner)
        pond_rect = pygame.Rect(20, GRID_HEIGHT - 120, 100, 100)
        pygame.draw.ellipse(self.screen, LOTUS_POND_COLOR, pond_rect)
        pygame.draw.ellipse(self.screen, (40, 80, 100), pond_rect, 2)
        
        # Lotus flowers on pond
        lotus_positions = [(50, GRID_HEIGHT - 80), (80, GRID_HEIGHT - 60)]
        for lx, ly in lotus_positions:
            # Petals
            for angle in range(0, 360, 60):
                import math
                petal_x = lx + math.cos(math.radians(angle)) * 8
                petal_y = ly + math.sin(math.radians(angle)) * 8
                pygame.draw.circle(self.screen, LOTUS_FLOWER_COLOR, 
                                 (int(petal_x), int(petal_y)), 5)
            # Center
            pygame.draw.circle(self.screen, (255, 215, 100), (lx, ly), 4)
        
        # Buddha statue (top left corner)
        buddha_x, buddha_y = 60, 50
        # Base
        pygame.draw.rect(self.screen, BUDDHA_STATUE_COLOR,
                        (buddha_x - 15, buddha_y + 20, 30, 10))
        # Body
        pygame.draw.ellipse(self.screen, BUDDHA_STATUE_COLOR,
                           (buddha_x - 12, buddha_y, 24, 30))
        # Head
        pygame.draw.circle(self.screen, BUDDHA_STATUE_COLOR, 
                          (buddha_x, buddha_y - 5), 10)
        
        # Monks in orange robes (top right area, near spawn)
        monk_positions = [(GRID_WIDTH - 60, 40), (GRID_WIDTH - 100, 70)]
        for mx, my in monk_positions:
            # Robe
            pygame.draw.circle(self.screen, MONK_ROBE_COLOR, (mx, my + 5), 8)
            # Head
            pygame.draw.circle(self.screen, (220, 180, 140), (mx, my - 5), 5)
    
    def draw_boss_health_bar(self, boss):
        """Draw a large boss health bar across the top of the battlefield"""
        bar_width = 400
        bar_height = 22
        bar_x = (GRID_WIDTH - bar_width) // 2
        bar_y = 30

        # Frame and empty bar
        pygame.draw.rect(self.screen, (0, 0, 0), (bar_x - 3, bar_y - 3, bar_width + 6, bar_height + 6))
        pygame.draw.rect(self.screen, GOLD, (bar_x - 3, bar_y - 3, bar_width + 6, bar_height + 6), 2)
        pygame.draw.rect(self.screen, (80, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Current health - red, then orange, then yellow as it weakens
        health_percent = boss.health / boss.max_health
        if health_percent > 0.6:
            color = (200, 0, 0)
        elif health_percent > 0.3:
            color = (200, 100, 0)
        else:
            color = (200, 200, 0)
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(bar_width * health_percent), bar_height))

        # Boss name above, health numbers on the bar
        name_text = self.font_medium.render(boss.name, True, GOLD)
        self.screen.blit(name_text, name_text.get_rect(center=(GRID_WIDTH // 2, bar_y - 14)))
        health_text = self.font_small.render(f"{int(boss.health)} / {boss.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, health_text.get_rect(center=(GRID_WIDTH // 2, bar_y + bar_height // 2)))

    def draw_selected_tower_highlight(self):
        """Draw highlight around the selected tower or wall"""
        selected = self.selected_tower or self.selected_wall
        if not selected:
            return

        # Pulsing yellow border
        import math
        pulse = abs(math.sin(pygame.time.get_ticks() / 200))
        color = (255, 255, int(100 + pulse * 155))

        tower_rect = pygame.Rect(
            selected.x - selected.size // 2 - 4,
            selected.y - selected.size // 2 - 4,
            selected.size + 8,
            selected.size + 8
        )
        pygame.draw.rect(self.screen, color, tower_rect, 3)
    
    def draw_grid(self):
        """Draw the grid lines"""
        for x in range(0, GRID_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (x, 0), (x, GRID_HEIGHT))
        for y in range(0, GRID_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (0, y), (GRID_WIDTH, y))
    
    def draw_tower_preview(self):
        """Draw preview of tower/wall being placed"""
        # Don't show preview if cursor is cleared
        if self.build_mode is None or self.selected_tower_type is None:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if mouse_x < GRID_WIDTH and mouse_y < GRID_HEIGHT:
            grid_x = mouse_x // TILE_SIZE
            grid_y = mouse_y // TILE_SIZE
            
            # Check if valid position
            is_valid = self.is_valid_build_position(grid_x, grid_y)
            
            # Check if can afford
            if self.build_mode == 'tower':
                stats = TOWER_STATS[self.selected_tower_type]
                can_afford = self.resources.can_afford(
                    merit=stats['cost_merit'],
                    concentration=stats['cost_concentration'],
                    mindfulness=stats['cost_mindfulness']
                )
            else:  # wall mode
                can_afford = self.resources.can_afford(
                    merit=WALL_COST_MERIT,
                    concentration=WALL_COST_CONCENTRATION
                )
            
            # Draw preview
            preview_x = grid_x * TILE_SIZE
            preview_y = grid_y * TILE_SIZE
            
            if is_valid and can_afford:
                color = (100, 255, 100, 100)  # Green
            else:
                color = (255, 100, 100, 100)  # Red
            
            preview_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(preview_surface, color, (0, 0, TILE_SIZE, TILE_SIZE))
            self.screen.blit(preview_surface, (preview_x, preview_y))
    
    def draw_perfect_wave_message(self):
        """Draw perfect wave bonus message"""
        message = "PERFECT WAVE! +Mindfulness"
        text = self.font_large.render(message, True, (100, 255, 255))
        
        # Pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() / 200))
        alpha = int(200 + pulse * 55)
        
        # Center of screen
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # Background
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 100, 150, alpha), bg_surface.get_rect())
        self.screen.blit(bg_surface, bg_rect)
        
        # Text
        self.screen.blit(text, text_rect)
    
    def draw_feedback_message(self):
        """Draw feedback message (tower placed, can't afford, etc)"""
        text = self.font_medium.render(self.feedback_message, True, self.feedback_color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Background
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect())
        self.screen.blit(bg_surface, bg_rect)
        
        # Text
        self.screen.blit(text, text_rect)
    
    def draw_ability_objects(self):
        """Draw clickable ability objects"""
        mouse_pos = pygame.mouse.get_pos()
        cooldowns = self.abilities.get_all_cooldowns()
        
        # Lotus, Buddha, Monk positions
        positions = [
            (LOTUS_POND_POS, (255, 200, 255), 'metta'),
            (BUDDHA_STATUE_POS, (100, 200, 255), 'samadhi'),
            (MONK_POS, (255, 150, 50), 'karuna')
        ]

        for grid_pos, color, key in positions:
            x = grid_pos[0] * TILE_SIZE + TILE_SIZE // 2
            y = grid_pos[1] * TILE_SIZE + TILE_SIZE // 2
            self.draw_ability_object(x, y, color, key, cooldowns[key], mouse_pos)

    def draw_ability_icon(self, ability_key, x, y):
        """Draw a small picture for each ability (the font can't draw emoji)"""
        x, y = int(x), int(y)
        if ability_key == 'metta':
            # Lotus flower - six petals around a gold centre
            for angle in range(0, 360, 60):
                petal_x = x + int(math.cos(math.radians(angle)) * 7)
                petal_y = y + int(math.sin(math.radians(angle)) * 7)
                pygame.draw.circle(self.screen, (255, 255, 255), (petal_x, petal_y), 4)
            pygame.draw.circle(self.screen, (255, 215, 100), (x, y), 4)
        elif ability_key == 'samadhi':
            # Seated meditator - head above a triangle body
            pygame.draw.polygon(self.screen, (255, 255, 255), [(x - 10, y + 10), (x + 10, y + 10), (x, y - 3)])
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y - 8), 5)
        else:
            # Monk - shaved head above a saffron robe
            pygame.draw.ellipse(self.screen, (160, 70, 20), (x - 10, y - 1, 20, 13))
            pygame.draw.circle(self.screen, (225, 185, 145), (x, y - 6), 6)

    def draw_ability_object(self, x, y, color, ability_key, cooldown, mouse_pos):
        """Draw single ability object"""
        ability = self.abilities.get_ability(ability_key)
        radius = ABILITY_OBJECT_SIZE // 2
        is_hovered = self.point_in_circle(mouse_pos[0], mouse_pos[1], x, y, radius)
        can_use, reason = ability.can_use(self.resources)
        
        # Circle with pulse if ready
        if can_use:
            circle_color = color
            pulse = radius + int(2 * math.sin(pygame.time.get_ticks() / 300))
        else:
            circle_color = (80, 80, 80)
            pulse = radius
        
        pygame.draw.circle(self.screen, circle_color, (int(x), int(y)), pulse)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y)), pulse, 2)
        
        # Icon
        self.draw_ability_icon(ability_key, x, y)
        
        # Cooldown timer
        if cooldown > 0:
            timer = self.font_small.render(f"{int(cooldown)}s", True, (255, 255, 100))
            self.screen.blit(timer, timer.get_rect(center=(x, y + radius + 12)))
        
        # Uses remaining indicator (top right of circle)
        uses_text = self.font_small.render(f"{ability.uses_remaining}/3", True, (255, 255, 255))
        uses_bg = pygame.Rect(x + radius - 15, y - radius - 5, 30, 18)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), uses_bg)
        self.screen.blit(uses_text, uses_text.get_rect(center=(x + radius, y - radius + 4)))
        
        # Tooltip on hover
        if is_hovered:
            self.draw_ability_tooltip(x, y - 100, ability, can_use, reason)
    
    def draw_ability_tooltip(self, x, y, ability, can_use, reason):
        """Draw ability tooltip"""
        lines = [
            (ability.name, (255, 255, 255)),
            (f"Uses: {ability.uses_remaining}/3", (100, 255, 100) if ability.uses_remaining > 0 else (255, 100, 100)),
            (f"Cost: {ability.cost_merit}M {ability.cost_concentration}C {ability.cost_mindfulness}F", (200, 200, 200)),
            (f"CD: {int(ability.cooldown)}s", (200, 200, 200))
        ]
        if not can_use:
            lines.append((reason, (255, 100, 100)))
        
        # Background
        tooltip = pygame.Rect(x - 100, y, 200, len(lines) * 20 + 10)
        pygame.draw.rect(self.screen, (30, 40, 30), tooltip)
        pygame.draw.rect(self.screen, (200, 200, 100) if can_use else (150, 50, 50), tooltip, 2)
        
        # Text
        for i, (text, color) in enumerate(lines):
            rendered = self.font_small.render(text, True, color)
            self.screen.blit(rendered, (tooltip.x + 10, tooltip.y + 5 + i * 20))
    
    def draw_ui(self):
        """Draw UI panel"""
        # UI background
        ui_rect = pygame.Rect(UI_PANEL_X, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, UI_BG, ui_rect)
        pygame.draw.line(self.screen, GRID_LINE, (UI_PANEL_X, 0), 
                        (UI_PANEL_X, SCREEN_HEIGHT), 2)
        
        # Title
        title = self.font_large.render("Mara's Siege", True, GOLD)
        self.screen.blit(title, (UI_PANEL_X + 10, 10))
        
        # Resources - with better spacing
        y_pos = 60
        resources = self.resources.get_resources()
        
        merit_text = self.font_small.render(f"Merit (M): {resources['merit']}", True, GOLD)
        self.screen.blit(merit_text, (UI_PANEL_X + 10, y_pos))
        
        conc_text = self.font_small.render(f"Concentration (C): {resources['concentration']}", 
                                          True, ORANGE)
        self.screen.blit(conc_text, (UI_PANEL_X + 10, y_pos + 25))  # Was 22, now 25
        
        mind_text = self.font_small.render(f"Mindfulness (F): {resources['mindfulness']}", 
                                          True, BLUE)
        self.screen.blit(mind_text, (UI_PANEL_X + 10, y_pos + 50))  # Was 44, now 50
        
        # Wave info - moved down to avoid overlap
        y_pos = 160  # Was 150, now 160
        wave_info = self.wave_manager.get_wave_info()
        wave_text = self.font_medium.render(
            f"Wave {wave_info['current']}/{wave_info['total']}", 
            True, TEXT_COLOR
        )
        self.screen.blit(wave_text, (UI_PANEL_X + 10, y_pos))
        
        if not wave_info['in_progress']:
            time_text = self.font_small.render(
                f"Next: {int(wave_info['time_until_next'])}s",
                True, TEXT_COLOR
            )
            self.screen.blit(time_text, (UI_PANEL_X + 10, y_pos + 30))
        else:
            enemies_text = self.font_small.render(
                f"Enemies: {wave_info['enemies_alive'] + wave_info['enemies_queued']}",
                True, TEXT_COLOR
            )
            self.screen.blit(enemies_text, (UI_PANEL_X + 10, y_pos + 30))
        
        # Tower selection OR Wall mode
        y_pos = 215  # Moved up since controls removed
        if self.build_mode == 'tower':
            select_title = self.font_medium.render("Build Tower:", True, TEXT_COLOR)
        else:
            select_title = self.font_medium.render("Build Wall (15M 5C):", True, WALL_COLOR)
        self.screen.blit(select_title, (UI_PANEL_X + 10, y_pos))
        
        button_y = y_pos + 35
        if self.build_mode == 'tower':
            self.draw_tower_button('sati', UI_PANEL_X + 10, button_y)
            self.draw_tower_button('viriya', UI_PANEL_X + 10, button_y + 70)
            self.draw_tower_button('samadhi', UI_PANEL_X + 10, button_y + 140)
        else:
            # Show wall info
            wall_info = self.font_small.render("Place on paths to slow Mara" if self.map_mode == 'garden' else "Slows Mara that touch it", True, TEXT_COLOR)
            self.screen.blit(wall_info, (UI_PANEL_X + 10, button_y))
            wall_info2 = self.font_small.render("100 HP - Enemies attack it", True, TEXT_COLOR)
            self.screen.blit(wall_info2, (UI_PANEL_X + 10, button_y + 20))
            wall_info3 = self.font_small.render("Press W to switch modes", True, (180, 180, 180))
            self.screen.blit(wall_info3, (UI_PANEL_X + 10, button_y + 50))
        
        # Upgrade panel (if tower selected) - moved down significantly
        if self.selected_tower:
            y_pos = 520  # Was 430, moved down 90px!
            upgrade_title = self.font_medium.render("Selected Tower:", True, GOLD)
            self.screen.blit(upgrade_title, (UI_PANEL_X + 10, y_pos))
            
            # Tower info - better spacing
            tower_name = self.font_small.render(self.selected_tower.name, True, TEXT_COLOR)
            self.screen.blit(tower_name, (UI_PANEL_X + 10, y_pos + 28))  # Was 25, now 28
            
            level_text = self.font_small.render(
                f"Level: {self.selected_tower.level}/{self.selected_tower.max_level}",
                True, TEXT_COLOR
            )
            self.screen.blit(level_text, (UI_PANEL_X + 10, y_pos + 48))  # Was 43, now 48
            
            stats_text = self.font_small.render(
                f"Dmg:{int(self.selected_tower.damage)} Rng:{int(self.selected_tower.range)}",
                True, TEXT_COLOR
            )
            self.screen.blit(stats_text, (UI_PANEL_X + 10, y_pos + 68))  # Was 61, now 68
            
            # Upgrade info
            if self.selected_tower.can_upgrade():
                upgrade_info = self.selected_tower.get_upgrade_info()
                
                # Show upgrade costs with better spacing
                costs = []
                if upgrade_info['cost_merit'] > 0:
                    costs.append(f"{upgrade_info['cost_merit']}M")
                if upgrade_info['cost_concentration'] > 0:
                    costs.append(f"{upgrade_info['cost_concentration']}C")
                if upgrade_info['cost_mindfulness'] > 0:
                    costs.append(f"{upgrade_info['cost_mindfulness']}F")
                
                can_afford = self.resources.can_afford(
                    merit=upgrade_info['cost_merit'],
                    concentration=upgrade_info['cost_concentration'],
                    mindfulness=upgrade_info['cost_mindfulness']
                )
                
                cost_color = GOLD if can_afford else (150, 80, 80)
                cost_text = self.font_small.render(
                    f"Upgrade: {' '.join(costs)}",
                    True, cost_color
                )
                self.screen.blit(cost_text, (UI_PANEL_X + 10, y_pos + 90))  # Was 78, now 90
                
                # Right-click instruction
                hint_color = GOLD if can_afford else (150, 80, 80)
                hint_text = self.font_small.render(
                    "Right-click to upgrade",
                    True, hint_color
                )
                self.screen.blit(hint_text, (UI_PANEL_X + 10, y_pos + 112))  # Was 96, now 112

                sell_text = self.font_small.render("Hover + S to sell (50%)", True, (180, 180, 180))
                self.screen.blit(sell_text, (UI_PANEL_X + 10, y_pos + 134))
            else:
                max_text = self.font_small.render("MAX LEVEL", True, GOLD)
                self.screen.blit(max_text, (UI_PANEL_X + 10, y_pos + 90))  # Was 78, now 90

        # Wall panel (if wall selected) - same spot as the tower panel
        if self.selected_wall:
            wall = self.selected_wall
            y_pos = 520
            lines = [
                ("Selected Wall:", GOLD, self.font_medium),
                (f"Level: {wall.level}/{WALL_MAX_LEVEL}", TEXT_COLOR, self.font_small),
                (f"HP: {int(wall.health)}/{wall.max_health}", TEXT_COLOR, self.font_small),
                (wall.stats['effect'], (230, 140, 80), self.font_small),
            ]
            if wall.can_upgrade():
                cost_merit, cost_concentration = wall.get_upgrade_cost()
                can_afford = self.resources.can_afford(merit=cost_merit, concentration=cost_concentration)
                cost_color = GOLD if can_afford else (150, 80, 80)
                next_effect = WALL_LEVELS[wall.level + 1]['effect']
                lines.append((f"Upgrade: {cost_merit}M {cost_concentration}C", cost_color, self.font_small))
                lines.append((f"Next: {next_effect}", (180, 180, 180), self.font_small))
                lines.append(("Right-click to upgrade", cost_color, self.font_small))
            else:
                lines.append(("MAX LEVEL", GOLD, self.font_small))
            lines.append(("Hover + S to sell (50%)", (180, 180, 180), self.font_small))

            line_y = y_pos
            for text, color, font in lines:
                self.screen.blit(font.render(text, True, color), (UI_PANEL_X + 10, line_y))
                line_y += 26 if font == self.font_medium else 20

    def draw_tower_button(self, tower_type, x, y):
        """Draw a tower selection button"""
        stats = TOWER_STATS[tower_type]
        button_width = UI_PANEL_WIDTH - 20
        button_height = 60
        
        # Button background
        is_selected = (tower_type == self.selected_tower_type)
        if is_selected:
            border_color = GOLD
            border_width = 3
        else:
            border_color = GRID_LINE
            border_width = 1
        
        button_rect = pygame.Rect(x, y, button_width, button_height)
        pygame.draw.rect(self.screen, (40, 35, 50), button_rect)
        pygame.draw.rect(self.screen, border_color, button_rect, border_width)
        
        # Tower name
        name_text = self.font_small.render(stats['name'], True, stats['color'])
        self.screen.blit(name_text, (x + 5, y + 5))
        
        # Build costs (multiple resources)
        costs = []
        if stats['cost_merit'] > 0:
            costs.append(f"{stats['cost_merit']}M")
        if stats['cost_concentration'] > 0:
            costs.append(f"{stats['cost_concentration']}C")
        if stats['cost_mindfulness'] > 0:
            costs.append(f"{stats['cost_mindfulness']}F")
        
        cost_text = self.font_small.render(" ".join(costs), True, GOLD)
        self.screen.blit(cost_text, (x + 5, y + 23))
        
        # Stats
        stats_text = self.font_small.render(
            f"Dmg:{stats['damage']} Rng:{stats['range']}", 
            True, TEXT_COLOR
        )
        self.screen.blit(stats_text, (x + 5, y + 42))
    
    def draw_victory_screen(self):
        """Draw victory screen"""
        self.screen.fill(BACKGROUND)
        
        # Victory text
        victory_text = self.font_large.render("ENLIGHTENMENT ACHIEVED!", True, GOLD)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, text_rect)
        
        # Sub text
        sub_text = self.font_medium.render("You have defended against Mara's invasions", 
                                          True, TEXT_COLOR)
        sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(sub_text, sub_rect)
        
        # Stats
        resources = self.resources.get_resources()
        stats_text = self.font_small.render(
            f"Final Merit: {resources['merit']} | Waves: {self.wave_manager.current_wave}",
            True, TEXT_COLOR
        )
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(stats_text, stats_rect)
    
    def draw_defeat_screen(self):
        """Draw defeat screen"""
        self.screen.fill(BACKGROUND)
        
        # Defeat text
        defeat_text = self.font_large.render("MEDITATION BROKEN", True, (200, 50, 50))
        text_rect = defeat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(defeat_text, text_rect)
        
        # Reason
        if self.temple.is_destroyed():
            reason = "The temple has been destroyed"
        else:
            reason = "Too many Mara breached your defenses"
        
        reason_text = self.font_medium.render(reason, True, TEXT_COLOR)
        reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(reason_text, reason_rect)
        
        # Stats
        stats_text = self.font_small.render(
            f"Wave Reached: {self.wave_manager.current_wave} | Merit: {self.resources.merit}",
            True, TEXT_COLOR
        )
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(stats_text, stats_rect)
    
    def run(self):
        """Main game loop"""
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            self.handle_events()
            self.update(delta_time)
            self.draw()
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    pygame.mixer.pre_init(sounds.SAMPLE_RATE, -16, 1, 512)  # Mono audio for the generated sounds
    pygame.init()
    sounds.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mara's Siege")
    
    # Show main menu
    menu = MainMenu(screen)
    start_game, difficulty, map_mode = menu.run()
    
    # If player chose to start, run the game
    if start_game:
        game = Game(difficulty, map_mode)
        game.run()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
