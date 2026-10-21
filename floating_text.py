"""
Floating text system for damage numbers and resource rewards
"""
import pygame
import random

class FloatingText:
    """Text that floats up and fades away"""
    
    def __init__(self, x, y, text, color, size=24):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        
        # Animation properties
        self.lifetime = 1.5  # Seconds
        self.age = 0
        self.velocity_y = -50  # Pixels per second (float upward)
        self.velocity_x = random.uniform(-20, 20)  # Slight horizontal drift
        
        # Create font
        self.font = pygame.font.Font(None, size)
        
    def update(self, delta_time):
        """Update position and age"""
        self.age += delta_time
        self.y += self.velocity_y * delta_time
        self.x += self.velocity_x * delta_time
        
        # Slow down over time
        self.velocity_y *= 0.95
        
        return self.age < self.lifetime  # Return False when expired
    
    def draw(self, screen):
        """Draw the floating text"""
        # Calculate alpha based on age (fade out)
        alpha = int(255 * (1 - self.age / self.lifetime))
        
        # Render text
        text_surface = self.font.render(self.text, True, self.color)
        
        # Apply alpha
        text_surface.set_alpha(alpha)
        
        # Draw with slight outline for visibility
        # Outline (darker)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline = self.font.render(self.text, True, (0, 0, 0))
            outline.set_alpha(alpha // 2)
            screen.blit(outline, (self.x + dx, self.y + dy))
        
        # Main text
        screen.blit(text_surface, (self.x, self.y))


class FloatingTextManager:
    """Manages all floating text instances"""
    
    def __init__(self):
        self.texts = []
    
    def add_merit_gain(self, x, y, amount):
        """Add floating merit gain text"""
        text = f"+{amount}M"
        color = (255, 215, 0)  # Gold
        self.texts.append(FloatingText(x, y, text, color, size=28))
    
    def add_concentration_gain(self, x, y, amount):
        """Add floating concentration gain text"""
        text = f"+{amount}C"
        color = (255, 150, 50)  # Orange
        self.texts.append(FloatingText(x, y, text, color, size=24))
    
    def add_damage_number(self, x, y, damage):
        """Add floating damage number"""
        text = f"-{int(damage)}"
        color = (255, 100, 100)  # Red
        self.texts.append(FloatingText(x, y, text, color, size=20))
    
    def add_critical_hit(self, x, y, damage):
        """Add critical hit text (larger, different color)"""
        text = f"CRIT! -{int(damage)}"
        color = (255, 50, 50)  # Bright red
        self.texts.append(FloatingText(x, y, text, color, size=32))
    
    def add_text(self, x, y, text, color, size=24):
        """Add any floating message"""
        self.texts.append(FloatingText(x, y, text, color, size=size))
    
    def update(self, delta_time):
        """Update all floating texts"""
        self.texts = [text for text in self.texts if text.update(delta_time)]
    
    def draw(self, screen):
        """Draw all floating texts"""
        for text in self.texts:
            text.draw(screen)
    
    def clear(self):
        """Clear all floating texts"""
        self.texts.clear()
