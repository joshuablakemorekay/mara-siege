"""
Resource Manager for Mara's Siege
Handles Merit coins, Concentration points, and Mindfulness energy
"""

from config import STARTING_MERIT, STARTING_CONCENTRATION, STARTING_MINDFULNESS


class ResourceManager:
    """Manages the three resource types in the game"""
    
    def __init__(self):
        self.merit = STARTING_MERIT
        self.concentration = STARTING_CONCENTRATION
        self.mindfulness = STARTING_MINDFULNESS
        
        # Mindfulness regeneration - INCREASED!
        self.mindfulness_regen_rate = 0.5  # Was 0.1, now 0.5 per second = 30/minute!
        self.mindfulness_max = 100
    
    def can_afford(self, merit=0, concentration=0, mindfulness=0):
        """Check if player has enough resources"""
        return (self.merit >= merit and 
                self.concentration >= concentration and 
                self.mindfulness >= mindfulness)
    
    def spend(self, merit=0, concentration=0, mindfulness=0):
        """Spend resources if affordable"""
        if self.can_afford(merit, concentration, mindfulness):
            self.merit -= merit
            self.concentration -= concentration
            self.mindfulness -= mindfulness
            return True
        return False
    
    def add_merit(self, amount):
        """Add merit (from defeating enemies)"""
        self.merit += amount
    
    def add_concentration(self, amount):
        """Add concentration (from wave completion, combos)"""
        self.concentration += amount
    
    def add_mindfulness(self, amount):
        """Add mindfulness (rare, from perfect waves)"""
        self.mindfulness = min(self.mindfulness + amount, self.mindfulness_max)
    
    def regenerate_mindfulness(self, delta_time):
        """Slowly regenerate mindfulness over time"""
        self.mindfulness = min(
            self.mindfulness + self.mindfulness_regen_rate * delta_time,
            self.mindfulness_max
        )
    
    def wave_completion_bonus(self, wave_number, had_breaches):
        """Award resources for completing a wave"""
        # Concentration for completing wave - HUGE BONUS!
        concentration_bonus = 15 + (wave_number * 3)  # Was 10 + wave*2
        self.add_concentration(concentration_bonus)
        
        # Mindfulness bonus - ALWAYS GIVE SOME, more for perfect
        if not had_breaches:
            # Perfect wave - BIG BONUS!
            mindfulness_bonus = 8 + (wave_number // 2)
            self.add_mindfulness(mindfulness_bonus)
            return True  # Perfect wave
        else:
            # Had breaches but still give smaller bonus!
            mindfulness_bonus = 3 + (wave_number // 4)
            self.add_mindfulness(mindfulness_bonus)
            return False
    
    def get_resources(self):
        """Return current resource amounts"""
        return {
            'merit': int(self.merit),
            'concentration': int(self.concentration),
            'mindfulness': int(self.mindfulness)
        }
