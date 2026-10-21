"""
Wave Manager - Handles spawning waves of enemies
"""

import random
from config import (ENEMIES_PER_WAVE_BASE,
                   WAVE_DIFFICULTY_MULTIPLIER, BOSS_WAVES, FINAL_BOSS)
from enemy import (DoubtMara, CravingMara, DelusionMara, AngerMara,
                   IgnoranceMara, EnvyMara, PrideMara,
                   BossMaraLord, BossMaraTyrant)


class WaveManager:
    """Manages enemy waves and spawning"""
    
    def __init__(self, temple_position, paths, difficulty):
        self.difficulty = difficulty  # Settings dict from difficulty.py
        self.current_wave = 0
        self.wave_in_progress = False
        self.wave_complete = False
        self.time_until_next_wave = difficulty['wave_delay']
        self.breaches_this_wave = 0  # Track breaches per wave
        
        # Temple position for enemy targeting
        self.temple_position = temple_position
        self.paths = paths  # Each enemy picks one; the first is the boss route
        
        # Enemies
        self.enemies = []
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.spawn_interval = 0.8  # Seconds between each enemy spawn
        
        # Victory condition tracking - the final boss always comes on the last wave
        self.total_waves = difficulty['waves']
        self.boss_waves = dict(BOSS_WAVES)
        self.boss_waves[self.total_waves] = FINAL_BOSS
    
    def start_next_wave(self):
        """Start the next wave of enemies"""
        if self.wave_in_progress:
            return
        
        self.current_wave += 1
        self.wave_in_progress = True
        self.wave_complete = False
        self.breaches_this_wave = 0  # Reset breach counter
        
        # Calculate wave composition based on current wave
        num_enemies = int((ENEMIES_PER_WAVE_BASE + self.current_wave * 1.5) * self.difficulty['enemy_count_mult'])
        
        # Queue enemies to spawn with progressive introduction
        self.enemies_to_spawn = []
        
        for i in range(num_enemies):
            # Random path (each starts at its own spawn gate)
            path = random.choice(self.paths)
            
            # Progressive enemy type introduction
            enemy_type = self.select_enemy_type_for_wave()
            
            self.enemies_to_spawn.append((enemy_type, path))

        # Boss joins at the end of its wave, marching down the main road
        if self.current_wave in self.boss_waves:
            self.enemies_to_spawn.append((self.boss_waves[self.current_wave], self.paths[0]))

        self.spawn_timer = 0
    
    def select_enemy_type_for_wave(self):
        """Select appropriate enemy type based on current wave"""
        wave = self.current_wave
        
        # Waves 1-5: Basic enemies only
        if wave <= 5:
            return random.choice(['doubt', 'doubt', 'craving'])
        
        # Waves 6-8: Introduce Delusion
        elif wave <= 8:
            return random.choice(['doubt', 'craving', 'craving', 'delusion'])
        
        # Waves 9-11: Add Anger
        elif wave <= 11:
            return random.choice(['doubt', 'craving', 'delusion', 'delusion', 'anger'])
        
        # Waves 12-14: Add Ignorance
        elif wave <= 14:
            return random.choice(['craving', 'delusion', 'anger', 'anger', 'ignorance'])
        
        # Waves 15-17: Add Envy
        elif wave <= 17:
            return random.choice(['delusion', 'anger', 'ignorance', 'envy', 'envy'])
        
        # Waves 18-20: Add Pride + All types
        else:
            return random.choice([
                'doubt', 'craving', 'delusion', 'anger', 
                'ignorance', 'envy', 'pride', 'pride'
            ])
    
    def update(self, delta_time):
        """Update wave state"""
        if not self.wave_in_progress:
            # Countdown to next wave
            self.time_until_next_wave -= delta_time
            if self.time_until_next_wave <= 0:
                self.start_next_wave()
                self.time_until_next_wave = self.difficulty['wave_delay']
        else:
            # Spawn queued enemies
            if self.enemies_to_spawn:
                self.spawn_timer += delta_time
                if self.spawn_timer >= self.spawn_interval:
                    enemy_type, path = self.enemies_to_spawn.pop(0)
                    
                    # Create enemy based on type
                    if enemy_type == 'doubt':
                        enemy = DoubtMara(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'craving':
                        enemy = CravingMara(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'delusion':
                        enemy = DelusionMara(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'anger':
                        enemy = AngerMara(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'ignorance':
                        enemy = IgnoranceMara(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'envy':
                        enemy = EnvyMara(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'pride':
                        enemy = PrideMara(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'boss_mara_lord':
                        enemy = BossMaraLord(path, self.temple_position, self.current_wave)
                    elif enemy_type == 'boss_mara_tyrant':
                        enemy = BossMaraTyrant(path, self.temple_position, self.current_wave)
                    else:
                        enemy = DoubtMara(path, self.temple_position, self.current_wave)
                    
                    self.apply_difficulty(enemy)
                    self.enemies.append(enemy)
                    self.spawn_timer = 0
            
            # Update all enemies
            for enemy in self.enemies[:]:
                enemy.move()
            
            # Check if wave is complete
            if not self.enemies_to_spawn and not any(e.alive for e in self.enemies):
                self.wave_complete = True
                self.wave_in_progress = False
    
    def apply_difficulty(self, enemy):
        """Scale a new enemy's health, speed and rewards for the chosen difficulty"""
        enemy.max_health = int(enemy.max_health * self.difficulty['enemy_health_mult'])
        enemy.health = enemy.max_health
        enemy.base_speed *= self.difficulty['enemy_speed_mult']
        enemy.speed = enemy.base_speed
        enemy.merit_reward = max(1, round(enemy.merit_reward * self.difficulty['reward_mult']))
        enemy.concentration_reward = round(enemy.concentration_reward * self.difficulty['reward_mult'])
    
    def get_active_enemies(self):
        """Return list of alive enemies"""
        return [e for e in self.enemies if e.alive]
    
    def remove_dead_enemies(self):
        """Remove dead enemies and return merit rewards"""
        total_merit = 0
        total_concentration = 0
        for enemy in self.enemies[:]:
            if not enemy.alive and not enemy.reached_temple:
                total_merit += enemy.merit_reward
                # NEW! Also collect Concentration
                if hasattr(enemy, 'concentration_reward'):
                    total_concentration += enemy.concentration_reward
                self.enemies.remove(enemy)
        return total_merit, total_concentration
    
    def check_temple_breaches(self):
        """Check for enemies that reached the temple - returns the damage each one deals"""
        breaches = []
        for enemy in self.enemies[:]:
            if enemy.reached_temple:
                breaches.append(enemy.temple_damage)
                self.breaches_this_wave += 1
                self.enemies.remove(enemy)
        return breaches
    
    def is_victory(self):
        """Check if player completed all waves"""
        return self.current_wave >= self.total_waves and not self.wave_in_progress
    
    def was_perfect_wave(self):
        """Check if current wave had no breaches"""
        return self.breaches_this_wave == 0
    
    def get_wave_info(self):
        """Return current wave information"""
        return {
            'current': self.current_wave,
            'total': self.total_waves,
            'in_progress': self.wave_in_progress,
            'time_until_next': max(0, self.time_until_next_wave),
            'enemies_alive': len(self.get_active_enemies()),
            'enemies_queued': len(self.enemies_to_spawn)
        }
