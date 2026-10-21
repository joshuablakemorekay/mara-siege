"""
Wall system for blocking and redirecting enemy paths
"""
import pygame
from config import *

class Wall:
    """Wall that slows Mara - upgrades make it burn them, then block them completely"""
    
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # Position (center of tile)
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.size = WALL_SIZE
        
        # Level and health
        self.level = 1
        self.max_health = WALL_LEVELS[1]['health']
        self.health = self.max_health
        self.alive = True

    @property
    def stats(self):
        """Settings for this wall's current level"""
        return WALL_LEVELS[self.level]

    def can_upgrade(self):
        """Check if wall can be upgraded"""
        return self.level < WALL_MAX_LEVEL

    def get_upgrade_cost(self):
        """Merit and Concentration needed for the next level"""
        next_level = WALL_LEVELS[self.level + 1]
        return next_level['upgrade_merit'], next_level['upgrade_concentration']

    def upgrade(self):
        """Go up a level - extra health is added on top of current health"""
        if not self.can_upgrade():
            return
        self.level += 1
        extra = self.stats['health'] - self.max_health
        self.max_health = self.stats['health']
        self.health += extra

    def total_spent(self):
        """Merit and Concentration spent on this wall, including upgrades"""
        merit = WALL_COST_MERIT
        concentration = WALL_COST_CONCENTRATION
        for level in range(2, self.level + 1):
            merit += WALL_LEVELS[level]['upgrade_merit']
            concentration += WALL_LEVELS[level]['upgrade_concentration']
        return merit, concentration

    def take_damage(self, amount):
        """Take damage from enemy attacks"""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True  # Wall destroyed
        return False  # Still standing
    
    def get_health_percentage(self):
        """Get health as percentage"""
        return self.health / self.max_health
    
    def draw(self, screen):
        """Draw the wall"""
        # Calculate color based on health
        health_pct = self.get_health_percentage()
        
        if health_pct > 0.6:
            color = WALL_COLOR
        elif health_pct > 0.3:
            # Interpolate between normal and damaged
            t = (health_pct - 0.3) / 0.3
            color = tuple(
                int(WALL_DAMAGED_COLOR[i] * (1 - t) + WALL_COLOR[i] * t)
                for i in range(3)
            )
        else:
            color = WALL_DAMAGED_COLOR
        
        # Draw wall square
        wall_rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
        pygame.draw.rect(screen, color, wall_rect)

        # Brick lines from level 2, a red-hot glow at level 3
        if self.level >= 2:
            mid_y = wall_rect.centery
            pygame.draw.line(screen, (70, 55, 40), (wall_rect.left, mid_y), (wall_rect.right, mid_y), 2)
            pygame.draw.line(screen, (70, 55, 40), (wall_rect.centerx, wall_rect.top), (wall_rect.centerx, mid_y), 2)
            pygame.draw.line(screen, (70, 55, 40), (wall_rect.left + 10, mid_y), (wall_rect.left + 10, wall_rect.bottom), 2)
            pygame.draw.line(screen, (70, 55, 40), (wall_rect.right - 10, mid_y), (wall_rect.right - 10, wall_rect.bottom), 2)
        border_color = (230, 90, 40) if self.level >= 2 else (80, 80, 80)
        pygame.draw.rect(screen, border_color, wall_rect, 3 if self.level == 3 else 2)

        # Gold pips show the level
        for i in range(self.level):
            pygame.draw.circle(screen, GOLD, (wall_rect.x + 8 + i * 9, wall_rect.bottom - 7), 3)

        # Draw health bar if damaged
        if health_pct < 1.0:
            bar_width = self.size - 4
            bar_height = 4
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.size // 2 - 8
            
            # Background
            bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            
            # Health
            health_width = int(bar_width * health_pct)
            if health_width > 0:
                health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
                
                # Color based on health
                if health_pct > 0.5:
                    health_color = (100, 200, 100)
                elif health_pct > 0.25:
                    health_color = (200, 200, 50)
                else:
                    health_color = (200, 50, 50)
                
                pygame.draw.rect(screen, health_color, health_rect)
