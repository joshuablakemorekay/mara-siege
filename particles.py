"""
Particle System - Death effects and visual flourishes
"""

import pygame
import random
import math
from config import DEATH_PARTICLES, PARTICLE_LIFETIME


class Particle:
    """Individual particle for effects"""
    
    def __init__(self, x, y, color, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = PARTICLE_LIFETIME
        self.max_lifetime = PARTICLE_LIFETIME
        self.size = random.randint(3, 6)
    
    def update(self, delta_time):
        """Update particle position"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= delta_time
        
        # Gravity effect
        self.velocity_y += 0.2
    
    def is_alive(self):
        """Check if particle should still exist"""
        return self.lifetime > 0
    
    def draw(self, screen):
        """Draw the particle with fade"""
        if self.lifetime <= 0:
            return
        
        # Fade alpha based on lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))
        
        if size > 0:
            # Create surface with alpha
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, (size, size), size)
            screen.blit(particle_surface, (int(self.x - size), int(self.y - size)))


class ParticleSystem:
    """Manages all particles in the game"""
    
    def __init__(self):
        self.particles = []
    
    def create_death_explosion(self, x, y, color):
        """Create particle explosion when enemy dies"""
        for _ in range(DEATH_PARTICLES):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            # Vary particle color slightly
            varied_color = tuple(
                max(0, min(255, c + random.randint(-30, 30))) 
                for c in color
            )
            
            particle = Particle(x, y, varied_color, velocity_x, velocity_y)
            self.particles.append(particle)
    
    def update(self, delta_time):
        """Update all particles"""
        for particle in self.particles[:]:
            particle.update(delta_time)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        """Remove all particles"""
        self.particles.clear()
    
    def create_healing_effect(self, x, y):
        """Create healing particles (Metta Healing) - ENHANCED FOR SLOW-MO"""
        import random
        # TRIPLED particle count for visibility in slow-mo
        for _ in range(60):  # Was 20, now 60!
            angle = random.uniform(0, 6.28)
            speed = random.uniform(30, 80)  # Faster for more dramatic effect
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed - 40  # Float upward faster
            
            # Pink/white healing colors - brighter!
            color = (255, random.randint(200, 255), 230)
            particle = Particle(x, y, color, velocity_x, velocity_y)
            particle.size = random.randint(4, 8)  # Larger particles
            self.particles.append(particle)
    
    def create_freeze_wave(self, x, y):
        """Create freeze wave effect (Samadhi Wave) - ENHANCED FOR SLOW-MO"""
        import random
        # TRIPLED particle count
        for _ in range(90):  # Was 30, now 90!
            angle = random.uniform(0, 6.28)
            speed = random.uniform(60, 140)  # Much faster for explosive effect
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            # Blue freeze colors - brighter!
            color = (150, 200, 255)
            particle = Particle(x, y, color, velocity_x, velocity_y)
            particle.size = random.randint(4, 8)  # Larger
            self.particles.append(particle)
    
    def create_strike_wave(self):
        """Create strike wave effect (Karuna Strike) - ENHANCED FOR SLOW-MO"""
        import random
        # DOUBLED particle count across screen
        from config import GRID_WIDTH, GRID_HEIGHT
        for _ in range(100):  # Was 50, now 100!
            x = random.randint(0, GRID_WIDTH)
            y = random.randint(0, GRID_HEIGHT)
            velocity_x = random.uniform(-50, 50)  # Faster
            velocity_y = random.uniform(-50, 50)
            
            # Orange strike colors - brighter!
            color = (255, random.randint(120, 180), 50)
            particle = Particle(x, y, color, velocity_x, velocity_y)
            particle.size = random.randint(4, 8)  # Larger
            self.particles.append(particle)
