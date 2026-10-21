"""
Projectile - Attacks fired from towers at enemies
Enhanced with Buddhist-themed auras
"""

import pygame
import math
from config import PROJECTILE_SPEED, PROJECTILE_SIZE, PROJECTILE_COLOR, AURA_SIZE


class Projectile:
    """Projectile fired from towers"""
    
    def __init__(self, start_pos, target_enemy, damage, tower_type='sati'):
        self.x, self.y = start_pos
        self.target = target_enemy
        self.damage = damage
        self.speed = PROJECTILE_SPEED
        self.size = PROJECTILE_SIZE
        self.active = True
        self.tower_type = tower_type
        
        # Different colors/auras based on tower type
        if tower_type == 'sati':  # Mindfulness - Blue/calm
            self.color = (100, 200, 255)
            self.aura_color = (150, 220, 255)
        elif tower_type == 'viriya':  # Energy - Orange/fiery
            self.color = (255, 150, 50)
            self.aura_color = (255, 200, 100)
        elif tower_type == 'samadhi':  # Concentration - Purple/mystical
            self.color = (150, 100, 255)
            self.aura_color = (200, 150, 255)
        else:
            self.color = PROJECTILE_COLOR
            self.aura_color = (255, 255, 200)
        
        self.aura_pulse = 0  # For animated aura
    
    def update(self, delta_time=0.016):
        """Move projectile toward target"""
        if not self.active or not self.target.alive:
            self.active = False
            return
        
        # Animate aura pulse
        self.aura_pulse += delta_time * 10
        
        # Get target position
        target_x, target_y = self.target.get_position()
        
        # Calculate direction
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if hit target
        if distance < self.speed + 5:  # Hit radius
            self.target.take_damage(self.damage)
            self.active = False
            return
        
        # Move toward target
        if distance > 0:
            dx /= distance
            dy /= distance
            self.x += dx * self.speed
            self.y += dy * self.speed
    
    def draw(self, screen):
        """Draw the projectile with aura"""
        if not self.active:
            return
        
        # Draw pulsing aura (loving-kindness effect)
        pulse_size = AURA_SIZE + math.sin(self.aura_pulse) * 3
        aura_surface = pygame.Surface((int(pulse_size * 2), int(pulse_size * 2)), pygame.SRCALPHA)
        
        # Multiple aura layers for depth
        for i in range(3):
            alpha = 40 - i * 10
            size = pulse_size - i * 3
            pygame.draw.circle(aura_surface, (*self.aura_color, alpha),
                             (int(pulse_size), int(pulse_size)), int(size))
        
        screen.blit(aura_surface, 
                   (int(self.x - pulse_size), int(self.y - pulse_size)))
        
        # Draw core projectile
        pygame.draw.circle(screen, self.color,
                         (int(self.x), int(self.y)), self.size)
        
        # Bright center (wisdom/clarity)
        pygame.draw.circle(screen, (255, 255, 255),
                         (int(self.x), int(self.y)), self.size // 2)
