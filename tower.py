"""
Tower - Defense structures that attack enemies
Represents different Buddhist mental qualities
"""

import pygame
from config import TOWER_STATS, TILE_SIZE, TEXT_COLOR
from projectile import Projectile
import sounds


class Tower:
    """Base class for all defensive towers"""
    
    def __init__(self, grid_x, grid_y, tower_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = tower_type
        
        # Get stats from config
        stats = TOWER_STATS[tower_type]
        self.name = stats['name']
        self.base_damage = stats['damage']
        self.base_range = stats['range']
        self.fire_rate = stats['fire_rate']
        self.color = stats['color']
        
        # Upgrade system
        self.level = 1
        self.max_level = 3
        self.upgrade_cost_merit = stats['upgrade_cost_merit']
        self.upgrade_cost_concentration = stats['upgrade_cost_concentration']
        self.upgrade_cost_mindfulness = stats['upgrade_cost_mindfulness']
        self.upgrade_damage_bonus = stats['upgrade_damage']
        self.upgrade_range_bonus = stats['upgrade_range']
        
        # Current stats (base + upgrades)
        self.damage = self.base_damage
        self.range = self.base_range
        
        # Position (pixel coordinates - center of tile)
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.size = 30
        
        # Combat state
        self.target = None
        self.cooldown = 0
        self.projectiles = []
    
    def can_upgrade(self):
        """Check if tower can be upgraded"""
        return self.level < self.max_level
    
    def upgrade(self):
        """Upgrade the tower"""
        if not self.can_upgrade():
            return False
        
        self.level += 1
        self.damage = self.base_damage + (self.level - 1) * self.upgrade_damage_bonus
        self.range = self.base_range + (self.level - 1) * self.upgrade_range_bonus
        return True
    
    def get_upgrade_info(self):
        """Get upgrade information"""
        if not self.can_upgrade():
            return None
        
        next_damage = self.base_damage + self.level * self.upgrade_damage_bonus
        next_range = self.base_range + self.level * self.upgrade_range_bonus
        
        return {
            'cost_merit': self.upgrade_cost_merit,
            'cost_concentration': self.upgrade_cost_concentration,
            'cost_mindfulness': self.upgrade_cost_mindfulness,
            'next_damage': next_damage,
            'next_range': next_range,
            'current_level': self.level,
            'max_level': self.max_level
        }
    
    def update(self, delta_time, enemies):
        """Update tower state and shooting"""
        # Reduce cooldown
        if self.cooldown > 0:
            self.cooldown -= delta_time
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)
            if not projectile.active:
                self.projectiles.remove(projectile)
        
        # Find and attack enemies
        if self.cooldown <= 0:
            target = self.find_target(enemies)
            if target:
                self.shoot(target)
                self.cooldown = self.fire_rate
    
    def find_target(self, enemies):
        """Find closest enemy in range"""
        closest_enemy = None
        closest_distance = self.range + 1
        
        for enemy in enemies:
            if enemy.alive:
                distance = enemy.distance_to(self.x, self.y)
                if distance < self.range and distance < closest_distance:
                    closest_enemy = enemy
                    closest_distance = distance
        
        return closest_enemy
    
    def shoot(self, target):
        """Fire projectile at target"""
        projectile = Projectile((self.x, self.y), target, self.damage, self.type)
        self.projectiles.append(projectile)
        sounds.play('shoot')
    
    def draw(self, screen):
        """Draw the tower"""
        # Draw range circle (semi-transparent)
        range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*self.color, 30), 
                          (self.range, self.range), self.range)
        screen.blit(range_surface, 
                   (self.x - self.range, self.y - self.range))
        
        # Draw tower body
        tower_rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
        pygame.draw.rect(screen, self.color, tower_rect)
        
        # Draw border
        border_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.rect(screen, border_color, tower_rect, 2)
        
        # Draw tower top (triangle)
        top_points = [
            (self.x, self.y - self.size // 2 - 8),  # Top
            (self.x - 10, self.y - self.size // 2),  # Left
            (self.x + 10, self.y - self.size // 2)   # Right
        ]
        pygame.draw.polygon(screen, self.color, top_points)
        
        # Draw level indicator (gold dots - the font can't draw star symbols)
        if self.level > 1:
            start_x = self.x - (self.level - 1) * 4
            for i in range(self.level):
                pygame.draw.circle(screen, (255, 215, 0), (int(start_x + i * 8), int(self.y + self.size // 2 + 8)), 3)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # Cooldown indicator (small circle)
        if self.cooldown > 0:
            cooldown_percentage = self.cooldown / self.fire_rate
            cooldown_size = int(8 * cooldown_percentage)
            if cooldown_size > 0:
                pygame.draw.circle(screen, (255, 100, 100),
                                 (self.x, self.y), cooldown_size)


class SatiTower(Tower):
    """Mindfulness tower - balanced stats"""
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, 'sati')


class ViriyaTower(Tower):
    """Energy tower - fast attacks"""
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, 'viriya')


class SamadhiTower(Tower):
    """Concentration tower - slow but powerful"""
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, 'samadhi')
