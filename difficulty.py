"""
Difficulty settings for Mara's Siege
"""

DIFFICULTIES = {
    'easy': {
        'name': 'Novice Monk',
        'description': 'Learn the basics • Forgiving',
        'color': (100, 255, 100),  # Green
        'waves': 15,
        'wave_delay': 20.0,
        'starting_merit': 150,
        'starting_concentration': 50,
        'starting_mindfulness': 40,
        'enemy_health_mult': 0.8,
        'enemy_speed_mult': 0.9,
        'enemy_count_mult': 0.8,
        'reward_mult': 1.2,
        'wall_health_mult': 1.0
    },
    'normal': {
        'name': 'Temple Guardian',
        'description': 'Balanced challenge • Standard',
        'color': (255, 215, 0),  # Gold
        'waves': 20,
        'wave_delay': 15.0,
        'starting_merit': 120,
        'starting_concentration': 40,
        'starting_mindfulness': 30,
        'enemy_health_mult': 1.0,
        'enemy_speed_mult': 1.0,
        'enemy_count_mult': 1.0,
        'reward_mult': 1.0,
        'wall_health_mult': 1.0
    },
    'hard': {
        'name': 'Dharma Defender',
        'description': 'Challenging • Tight resources',
        'color': (255, 150, 50),  # Orange
        'waves': 25,
        'wave_delay': 12.0,
        'starting_merit': 100,
        'starting_concentration': 30,
        'starting_mindfulness': 20,
        'enemy_health_mult': 1.2,
        'enemy_speed_mult': 1.1,
        'enemy_count_mult': 1.3,
        'reward_mult': 0.9,
        'wall_health_mult': 1.0
    },
    'extreme': {
        'name': 'Enlightenment Trial',
        'description': 'Brutal • Masters only',
        'color': (255, 50, 50),  # Red
        'waves': 30,
        'wave_delay': 10.0,
        'starting_merit': 80,
        'starting_concentration': 25,
        'starting_mindfulness': 15,
        'enemy_health_mult': 1.5,
        'enemy_speed_mult': 1.25,
        'enemy_count_mult': 1.6,
        'reward_mult': 0.8,
        'wall_health_mult': 0.8
    }
}

# Default difficulty
DEFAULT_DIFFICULTY = 'normal'
