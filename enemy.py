"""
Enemy - Mara invaders that attack the temple
Enhanced with diverse enemy types, shapes, and movement patterns
"""

import pygame
import math
from config import ENEMY_STATS, TILE_SIZE, TEXT_COLOR


class Enemy:
    """Base class for all Mara enemies"""
    
    def __init__(self, enemy_type, path, target_position, wave_number=1):
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]

        # Path to walk (grid corners -> pixel centres), ending at the temple centre
        self.waypoints = [(gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2)
                          for gx, gy in path]
        self.waypoints.append(target_position)
        self.waypoint_index = 1

        # Position on the path's centre line, plus where we actually draw (with wobble)
        self.path_x, self.path_y = self.waypoints[0]
        self.x = self.path_x
        self.y = self.path_y
        
        # Stats (scale with wave number)
        wave_multiplier = 1 + (wave_number - 1) * 0.15
        if stats.get('is_boss', False):
            wave_multiplier = 1  # Boss health is set per boss
        self.max_health = int(stats['health'] * wave_multiplier)
        self.health = self.max_health
        self.base_speed = stats['speed']
        self.speed = self.base_speed
        self.merit_reward = stats['merit_reward']
        self.concentration_reward = stats.get('concentration_reward', 0)  # NEW!
        self.color = stats['color']
        self.name = stats['name']
        self.size = stats['size']
        self.shape = stats['shape']
        self.movement_type = stats['movement']
        
        # Special abilities
        self.armor = stats.get('armor', 0)  # Damage reduction
        self.tower_damage = stats.get('tower_damage', 0)
        self.merit_steal = stats.get('merit_steal', 0)
        self.metta_immune = stats.get('metta_immune', False)
        self.is_boss = stats.get('is_boss', False)
        self.temple_damage = stats.get('temple_damage', 10)
        
        # Ability effects
        self.frozen = False  # NEW! Samadhi Wave effect
        self.freeze_timer = 0  # NEW!
        
        # Movement pattern - a side-to-side wobble that stays inside the path
        self.movement_time = 0  # For time-based patterns
        self.zigzag_frequency = stats.get('zigzag_frequency', 0)
        self.serpentine_frequency = stats.get('serpentine_frequency', 0)

        # State
        self.alive = True
        self.reached_temple = False
        self.has_damaged_tower = False
    
    def take_damage(self, damage):
        """Enemy takes damage from tower (with armor consideration)"""
        actual_damage = damage * (1 - self.armor)
        self.health -= actual_damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
    
    def move(self):
        """Walk along the path toward the temple, wobbling in the enemy's own style"""
        if not self.alive:
            return

        # Check if frozen (Samadhi Wave ability)
        if self.frozen:
            self.freeze_timer -= 0.016  # Decrease timer
            if self.freeze_timer <= 0:
                self.frozen = False
            return  # Don't move while frozen!

        self.movement_time += 0.016  # Approximate delta time

        # Step along the path's centre line, turning at each corner
        step = self.speed
        dir_x, dir_y = 0, 0
        while step > 0 and self.waypoint_index < len(self.waypoints):
            target_x, target_y = self.waypoints[self.waypoint_index]
            dx = target_x - self.path_x
            dy = target_y - self.path_y
            distance = math.sqrt(dx**2 + dy**2)
            if distance == 0:
                self.waypoint_index += 1
                continue
            dir_x, dir_y = dx / distance, dy / distance
            if distance <= step:
                # Reach this corner and carry the rest of the step to the next one
                self.path_x, self.path_y = target_x, target_y
                step -= distance
                self.waypoint_index += 1
            else:
                self.path_x += dir_x * step
                self.path_y += dir_y * step
                step = 0

        # Side-to-side wobble, kept small so enemies stay on the path
        if self.movement_type == 'zigzag':
            offset = math.sin(self.movement_time * self.zigzag_frequency * 100) * 10
        elif self.movement_type == 'serpentine':
            offset = math.sin(self.movement_time * self.serpentine_frequency * 100) * 10
        elif self.movement_type == 'arc':
            offset = math.sin(self.movement_time * 1.5) * 6
        else:
            offset = 0
        self.x = self.path_x - dir_y * offset
        self.y = self.path_y + dir_x * offset

        # Reached the temple once the last waypoint (its centre) is done
        if self.waypoint_index >= len(self.waypoints):
            self.reached_temple = True
            self.alive = False

    def get_position(self):
        """Return current position"""
        return (self.x, self.y)
    
    def distance_to(self, x, y):
        """Calculate distance to a point"""
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx**2 + dy**2)
    
    def draw(self, screen):
        """Draw the enemy with shape-specific rendering"""
        if not self.alive:
            return
        
        # Draw enemy based on shape
        if self.shape == 'circle':
            self.draw_circle(screen)
        elif self.shape == 'triangle':
            self.draw_triangle(screen)
        elif self.shape == 'square':
            self.draw_square(screen)
        elif self.shape == 'blob':
            self.draw_blob(screen)
        elif self.shape == 'elongated':
            self.draw_elongated(screen)
        elif self.shape == 'crown':
            self.draw_crown(screen)
        
        # Draw name label
        self.draw_name_label(screen)
        
        # Draw health bar
        self.draw_health_bar(screen)
    
    def draw_circle(self, screen):
        """Draw circular enemy (Doubt, Craving)"""
        pygame.draw.circle(screen, self.color, 
                          (int(self.x), int(self.y)), self.size // 2)
        border_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.circle(screen, border_color,
                          (int(self.x), int(self.y)), self.size // 2, 2)
    
    def draw_triangle(self, screen):
        """Draw triangular enemy (Anger)"""
        half_size = self.size // 2
        points = [
            (int(self.x), int(self.y - half_size)),  # Top
            (int(self.x - half_size), int(self.y + half_size)),  # Bottom left
            (int(self.x + half_size), int(self.y + half_size))   # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)
        border_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.polygon(screen, border_color, points, 2)
    
    def draw_square(self, screen):
        """Draw square enemy (Ignorance)"""
        half_size = self.size // 2
        rect = pygame.Rect(
            int(self.x - half_size),
            int(self.y - half_size),
            self.size,
            self.size
        )
        pygame.draw.rect(screen, self.color, rect)
        border_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.rect(screen, border_color, rect, 2)
    
    def draw_blob(self, screen):
        """Draw irregular blob (Delusion)"""
        # Create wobbly circle with multiple circles
        base_radius = self.size // 2
        for i in range(5):
            angle = (i / 5) * 2 * math.pi + self.movement_time
            wobble = math.sin(self.movement_time * 3 + i) * 3
            offset_x = math.cos(angle) * wobble
            offset_y = math.sin(angle) * wobble
            radius = base_radius + int(math.sin(self.movement_time * 2 + i) * 3)
            
            pygame.draw.circle(screen, self.color,
                             (int(self.x + offset_x), int(self.y + offset_y)),
                             radius)
        
        # Border
        border_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.circle(screen, border_color,
                          (int(self.x), int(self.y)), base_radius, 2)
    
    def draw_elongated(self, screen):
        """Draw elongated/stretched shape (Envy)"""
        # Oval/ellipse shape
        rect = pygame.Rect(
            int(self.x - self.size // 2),
            int(self.y - self.size // 3),
            self.size,
            int(self.size * 0.6)
        )
        pygame.draw.ellipse(screen, self.color, rect)
        border_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.ellipse(screen, border_color, rect, 2)
    
    def draw_crown(self, screen):
        """Draw crown shape (Pride)"""
        half_size = self.size // 2
        
        # Base circle
        pygame.draw.circle(screen, self.color,
                          (int(self.x), int(self.y)), half_size)
        
        # Crown points on top
        crown_points = []
        for i in range(5):
            angle = (i / 5) * 2 * math.pi - math.pi / 2
            if i % 2 == 0:  # Peak
                radius = half_size + 8
            else:  # Valley
                radius = half_size
            
            px = self.x + math.cos(angle) * radius
            py = self.y + math.sin(angle) * radius
            crown_points.append((int(px), int(py)))
        
        pygame.draw.polygon(screen, self.color, crown_points)
        
        # Border
        border_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.circle(screen, border_color,
                          (int(self.x), int(self.y)), half_size, 2)
    
    def draw_name_label(self, screen):
        """Draw enemy name above sprite"""
        font = pygame.font.Font(None, 16)
        name_text = font.render(self.name, True, TEXT_COLOR)
        name_rect = name_text.get_rect(center=(int(self.x), int(self.y - self.size - 15)))
        
        # Name background for readability
        bg_rect = name_rect.inflate(4, 2)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 150), bg_surface.get_rect())
        screen.blit(bg_surface, bg_rect)
        screen.blit(name_text, name_rect)
    
    def draw_health_bar(self, screen):
        """Draw health bar"""
        health_bar_width = 30
        health_bar_height = 4
        health_bar_x = int(self.x - health_bar_width // 2)
        health_bar_y = int(self.y - self.size - 5)
        
        # Background
        pygame.draw.rect(screen, (50, 30, 30),
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Current health
        health_percentage = self.health / self.max_health
        current_health_width = int(health_bar_width * health_percentage)
        
        if health_percentage > 0.5:
            health_color = (50, 200, 50)
        elif health_percentage > 0.25:
            health_color = (220, 200, 50)
        else:
            health_color = (200, 50, 50)
        
        if current_health_width > 0:
            pygame.draw.rect(screen, health_color,
                            (health_bar_x, health_bar_y, current_health_width, health_bar_height))


# Enemy type classes
class DoubtMara(Enemy):
    """Slow moving basic enemy"""
    def __init__(self, path, target_position, wave_number=1):
        super().__init__('doubt', path, target_position, wave_number)


class CravingMara(Enemy):
    """Fast moving enemy with less health"""
    def __init__(self, path, target_position, wave_number=1):
        super().__init__('craving', path, target_position, wave_number)


class DelusionMara(Enemy):
    """Zig-zagging enemy, hard to predict"""
    def __init__(self, path, target_position, wave_number=1):
        super().__init__('delusion', path, target_position, wave_number)


class AngerMara(Enemy):
    """Fast aggressive enemy that damages towers"""
    def __init__(self, path, target_position, wave_number=1):
        super().__init__('anger', path, target_position, wave_number)


class IgnoranceMara(Enemy):
    """Heavily armored slow tank"""
    def __init__(self, path, target_position, wave_number=1):
        super().__init__('ignorance', path, target_position, wave_number)


class EnvyMara(Enemy):
    """Serpentine moving enemy that steals merit"""
    def __init__(self, path, target_position, wave_number=1):
        super().__init__('envy', path, target_position, wave_number)


class PrideMara(Enemy):
    """Arc-moving elite enemy immune to conversion"""
    def __init__(self, path, target_position, wave_number=1):
        super().__init__('pride', path, target_position, wave_number)


class BossMaraLord(Enemy):
    """First boss - Wave 10"""
    def __init__(self, path, target_position, wave_number=10):
        super().__init__('boss_mara_lord', path, target_position, wave_number)


class BossMaraTyrant(Enemy):
    """Final boss - Wave 20"""
    def __init__(self, path, target_position, wave_number=20):
        super().__init__('boss_mara_tyrant', path, target_position, wave_number)
