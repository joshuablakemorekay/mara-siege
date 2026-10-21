"""
Special Abilities System for Mara's Siege
"""
import pygame
import time

class Ability:
    """Base class for special abilities"""
    
    def __init__(self, name, cost_merit, cost_concentration, cost_mindfulness, cooldown, max_uses=3):
        self.name = name
        self.cost_merit = cost_merit
        self.cost_concentration = cost_concentration
        self.cost_mindfulness = cost_mindfulness
        self.cooldown = cooldown
        self.max_uses = max_uses
        
        # State
        self.last_used = 0
        self.is_ready = True
        self.uses_remaining = max_uses
        self.times_used = 0
    
    def can_use(self, resources):
        """Check if ability can be used"""
        # Check uses remaining
        if self.uses_remaining <= 0:
            return False, "No uses left"
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_used < self.cooldown:
            return False, "On cooldown"
        
        # Check resources
        if not resources.can_afford(
            merit=self.cost_merit,
            concentration=self.cost_concentration,
            mindfulness=self.cost_mindfulness
        ):
            return False, "Not enough resources"
        
        return True, "Ready"
    
    def use(self, resources):
        """Use the ability (spend resources and start cooldown)"""
        resources.spend(
            merit=self.cost_merit,
            concentration=self.cost_concentration,
            mindfulness=self.cost_mindfulness
        )
        self.last_used = time.time()
        self.is_ready = False
        self.uses_remaining -= 1
        self.times_used += 1
    
    def get_cooldown_remaining(self):
        """Get remaining cooldown time"""
        current_time = time.time()
        elapsed = current_time - self.last_used
        remaining = max(0, self.cooldown - elapsed)
        
        if remaining == 0:
            self.is_ready = True
        
        return remaining
    
    def execute(self, game):
        """Execute ability effect - override in subclasses"""
        pass


class MettaHealing(Ability):
    """Ability 1: Heal the temple - PROGRESSIVE POWER"""
    
    def __init__(self):
        super().__init__(
            name="Metta Healing",
            cost_merit=50,
            cost_concentration=0,
            cost_mindfulness=30,
            cooldown=30.0,  # Reduced from 60s
            max_uses=3
        )
        # Progressive healing: 10 → 15 → 25 (matches breach damage!)
        self.heal_amounts = [10, 15, 25]
    
    def execute(self, game):
        """Heal the temple with increasing power"""
        # Get heal amount based on use count
        use_index = self.times_used - 1  # -1 because we already incremented
        heal_amount = self.heal_amounts[min(use_index, len(self.heal_amounts) - 1)]
        
        game.temple.heal(heal_amount)
        game.show_message(f"Metta Healing! +{heal_amount} HP (Use {self.times_used}/3)", (255, 200, 255))
        
        # Trigger LONGER slow motion - scales with use number!
        duration = 2.5 + (self.times_used * 0.5)  # 3s, 3.5s, 4s
        game.trigger_slow_motion(duration)
        
        # Create MASSIVE healing particles (MORE for each use!)
        burst_count = 3 + self.times_used  # 4, 5, 6 bursts!
        for _ in range(burst_count):
            game.particle_system.create_healing_effect(
                game.temple.x,
                game.temple.y
            )


class SamadhiWave(Ability):
    """Ability 2: Freeze all enemies"""
    
    def __init__(self):
        super().__init__(
            name="Samadhi Wave",
            cost_merit=0,
            cost_concentration=40,
            cost_mindfulness=40,
            cooldown=40.0,  # Reduced from 90s
            max_uses=3
        )
        self.freeze_duration = 5.0
    
    def execute(self, game):
        """Freeze all enemies"""
        # Mark all enemies as frozen
        frozen_count = 0
        for enemy in game.wave_manager.enemies:
            enemy.frozen = True
            enemy.freeze_timer = self.freeze_duration
            frozen_count += 1
        
        game.show_message(f"Samadhi Wave! {frozen_count} enemies frozen (Use {self.times_used}/3)", (100, 200, 255))
        
        # Trigger LONGER slow motion - scales with use!
        duration = 3.0 + (self.times_used * 0.5)  # 3.5s, 4s, 4.5s!
        game.trigger_slow_motion(duration)
        
        # Create MASSIVE freeze wave (MORE for each use!)
        burst_count = 4 + self.times_used  # 5, 6, 7 bursts!
        for i in range(burst_count):
            game.particle_system.create_freeze_wave(
                game.temple.x,
                game.temple.y
            )


class KarunaStrike(Ability):
    """Ability 3: Damage all enemies"""
    
    def __init__(self):
        super().__init__(
            name="Karuna Strike",
            cost_merit=60,
            cost_concentration=50,
            cost_mindfulness=0,
            cooldown=35.0,  # Reduced from 75s
            max_uses=3
        )
        self.damage = 30
    
    def execute(self, game):
        """Damage all enemies on screen"""
        enemies_hit = 0
        for enemy in game.wave_manager.enemies:
            enemy.take_damage(self.damage)
            enemies_hit += 1
            
            # Show damage numbers
            game.floating_text.add_damage_number(enemy.x, enemy.y - 30, self.damage)
        
        if enemies_hit > 0:
            game.show_message(f"Karuna Strike! {enemies_hit} enemies hit (Use {self.times_used}/3)", (255, 150, 50))
        
        # Trigger LONGER slow motion - scales with use!
        duration = 2.5 + (self.times_used * 0.5)  # 3s, 3.5s, 4s!
        game.trigger_slow_motion(duration)
        
        # Create MASSIVE strike wave (MORE for each use!)
        burst_count = 3 + self.times_used  # 4, 5, 6 bursts!
        for _ in range(burst_count):
            game.particle_system.create_strike_wave()


class AbilityManager:
    """Manages all special abilities"""
    
    def __init__(self):
        self.abilities = {
            'metta': MettaHealing(),
            'samadhi': SamadhiWave(),
            'karuna': KarunaStrike()
        }
    
    def get_ability(self, key):
        """Get ability by key"""
        return self.abilities.get(key)
    
    def can_use(self, key, resources):
        """Check if ability can be used"""
        ability = self.abilities.get(key)
        if ability:
            return ability.can_use(resources)
        return False, "Unknown ability"
    
    def use_ability(self, key, resources, game):
        """Use an ability"""
        ability = self.abilities.get(key)
        if not ability:
            return False
        
        can_use, reason = ability.can_use(resources)
        if not can_use:
            game.show_message(f"{ability.name}: {reason}", (255, 100, 100))
            return False
        
        # Use ability
        ability.use(resources)
        ability.execute(game)
        return True
    
    def get_all_cooldowns(self):
        """Get cooldown info for all abilities"""
        return {
            key: ability.get_cooldown_remaining()
            for key, ability in self.abilities.items()
        }
