"""
Temple - The central structure to protect
Represents the meditator's pure mind
"""

import pygame
from config import (TEMPLE_HEALTH, TEMPLE_SIZE, TEMPLE_POSITION, 
                   TILE_SIZE, TEMPLE_COLOR, TEXT_COLOR)


class Temple:
    """The central temple that must be protected"""
    
    def __init__(self):
        self.grid_x, self.grid_y = TEMPLE_POSITION
        self.x = self.grid_x * TILE_SIZE
        self.y = self.grid_y * TILE_SIZE
        self.max_health = TEMPLE_HEALTH
        self.health = self.max_health
        self.size = TEMPLE_SIZE
        
        # For tracking breaches (meditation broken condition)
        self.breaches = 0
        self.max_breaches = 10
    
    def take_damage(self, damage):
        """Temple takes damage from Mara"""
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def heal(self, amount):
        """Heal the temple (Metta Healing ability)"""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
    
    def register_breach(self, damage=10):
        """Enemy reached temple area"""
        self.breaches += 1
        self.take_damage(damage)  # Bosses hit harder than normal Mara
    
    def is_destroyed(self):
        """Check if temple is destroyed"""
        return self.health <= 0
    
    def meditation_broken(self):
        """Check if too many breaches occurred"""
        return self.breaches >= self.max_breaches
    
    def get_center(self):
        """Return center coordinates of temple"""
        return (self.x + self.size // 2, self.y + self.size // 2)
    
    def draw(self, screen):
        """Draw the temple"""
        # Main temple body (golden rectangle)
        temple_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(screen, TEMPLE_COLOR, temple_rect)
        pygame.draw.rect(screen, (200, 150, 50), temple_rect, 3)  # Border
        
        # Draw roof/stupa on top
        roof_points = [
            (self.x + self.size // 2, self.y - 10),  # Top point
            (self.x, self.y),  # Left
            (self.x + self.size, self.y)  # Right
        ]
        pygame.draw.polygon(screen, (220, 180, 80), roof_points)
        
        # Health bar
        health_bar_width = self.size
        health_bar_height = 8
        health_bar_x = self.x
        health_bar_y = self.y - 25
        
        # Background (red)
        pygame.draw.rect(screen, (100, 30, 30), 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health (green/yellow/red based on percentage)
        health_percentage = self.health / self.max_health
        current_health_width = int(health_bar_width * health_percentage)
        
        if health_percentage > 0.6:
            health_color = (50, 200, 50)  # Green
        elif health_percentage > 0.3:
            health_color = (220, 200, 50)  # Yellow
        else:
            health_color = (200, 50, 50)  # Red
        
        pygame.draw.rect(screen, health_color,
                        (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        
        # Health text
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"{int(self.health)}/{self.max_health}", True, TEXT_COLOR)
        screen.blit(health_text, (health_bar_x + 5, health_bar_y - 20))
        
        # Breaches counter
        breach_text = font.render(f"Breaches: {self.breaches}/{self.max_breaches}", 
                                 True, TEXT_COLOR)
        screen.blit(breach_text, (self.x, self.y + self.size + 10))
