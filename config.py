"""
Mara's Siege - Configuration File
Contains all game constants, colors, and settings
"""

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Grid settings
GRID_COLS = 20
GRID_ROWS = 14
TILE_SIZE = 40
GRID_WIDTH = GRID_COLS * TILE_SIZE  # 800
GRID_HEIGHT = GRID_ROWS * TILE_SIZE  # 560

# UI Panel (right side)
UI_PANEL_WIDTH = SCREEN_WIDTH - GRID_WIDTH  # 200
UI_PANEL_X = GRID_WIDTH

# Colors - Buddhist meditation garden themed
BACKGROUND = (35, 50, 40)  # Deep garden green
GRID_LINE = (50, 70, 60)
BUILDABLE = (40, 60, 50)

# Meditation Garden Elements
LOTUS_POND_COLOR = (60, 100, 120)  # Water blue
LOTUS_FLOWER_COLOR = (255, 200, 220)  # Pink lotus
BUDDHA_STATUE_COLOR = (180, 150, 100)  # Stone/bronze
MONK_ROBE_COLOR = (255, 140, 0)  # Saffron orange
GRASS_COLOR = (70, 120, 70)  # Lush grass

# UI Colors
UI_BG = (15, 10, 25)
TEXT_COLOR = (220, 210, 200)
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
BLUE = (100, 150, 255)

# Game Object Colors
TEMPLE_COLOR = (255, 215, 100)  # Golden
TOWER_COLOR = (100, 200, 255)  # Light blue
ENEMY_COLOR = (200, 50, 50)  # Dark red
PROJECTILE_COLOR = (255, 255, 150)  # Light yellow
WALL_COLOR = (100, 100, 120)  # Stone grey

# Temple settings
TEMPLE_HEALTH = 100
TEMPLE_SIZE = 80
TEMPLE_POSITION = (14, 7)  # Grid coordinates (center-right)

# Starting resources - Rebalanced for smoother early game
STARTING_MERIT = 120  # Increased from 80 - easier start!
STARTING_CONCENTRATION = 40
STARTING_MINDFULNESS = 30

# Tower costs and stats
TOWER_STATS = {
    'sati': {
        'name': 'Sati Tower',
        'cost_merit': 30,
        'cost_concentration': 0,
        'cost_mindfulness': 15,  # Mindfulness tower
        'damage': 15,
        'range': 120,
        'fire_rate': 1.0,
        'color': (100, 200, 255),
        'description': 'Mindfulness - Moderate damage, good range',
        'upgrade_cost_merit': 20,
        'upgrade_cost_concentration': 10,
        'upgrade_cost_mindfulness': 5,
        'upgrade_damage': 8,
        'upgrade_range': 20
    },
    'viriya': {
        'name': 'Viriya Tower',
        'cost_merit': 40,  # Merit only, most accessible
        'cost_concentration': 0,
        'cost_mindfulness': 0,
        'damage': 10,
        'range': 100,
        'fire_rate': 0.5,
        'color': (255, 150, 50),
        'description': 'Energy - Fast attacks, moderate damage',
        'upgrade_cost_merit': 25,
        'upgrade_cost_concentration': 8,
        'upgrade_cost_mindfulness': 0,
        'upgrade_damage': 5,
        'upgrade_range': 15
    },
    'samadhi': {
        'name': 'Samadhi Tower',
        'cost_merit': 35,
        'cost_concentration': 20,  # Concentration tower
        'cost_mindfulness': 0,
        'damage': 40,
        'range': 150,
        'fire_rate': 2.0,
        'color': (150, 100, 255),
        'description': 'Concentration - Slow, high damage',
        'upgrade_cost_merit': 30,
        'upgrade_cost_concentration': 15,
        'upgrade_cost_mindfulness': 8,
        'upgrade_damage': 20,
        'upgrade_range': 25
    }
}

# Wall stats
WALL_COST = 25
WALL_HEALTH = 100

# Enemy stats
ENEMY_STATS = {
    'doubt': {
        'name': 'Doubt Mara',
        'health': 50,
        'speed': 1.0,
        'merit_reward': 8,  # Increased from 5 for better early game
        'concentration_reward': 3,
        'color': (150, 50, 50),
        'size': 20,
        'shape': 'circle',
        'movement': 'straight'
    },
    'craving': {
        'name': 'Craving Mara',
        'health': 30,
        'speed': 1.8,
        'merit_reward': 6,  # Increased from 4 for better early game
        'concentration_reward': 2,
        'color': (200, 80, 80),
        'size': 20,
        'shape': 'circle',
        'movement': 'straight'
    },
    'delusion': {
        'name': 'Delusion Mara',
        'health': 60,
        'speed': 1.2,
        'merit_reward': 10,  # Increased from 7
        'concentration_reward': 4,
        'color': (120, 100, 150),  # Murky purple
        'size': 30,
        'shape': 'blob',
        'movement': 'zigzag',
        'zigzag_amplitude': 40,
        'zigzag_frequency': 0.05
    },
    'anger': {
        'name': 'Anger Mara',
        'health': 40,
        'speed': 2.0,
        'merit_reward': 11,  # Increased from 8
        'concentration_reward': 5,
        'color': (220, 60, 30),  # Burning red
        'size': 24,
        'shape': 'triangle',
        'movement': 'straight',
        'tower_damage': 5  # Damages towers on contact
    },
    'ignorance': {
        'name': 'Ignorance Mara',
        'health': 120,
        'speed': 0.8,
        'merit_reward': 14,  # Increased from 10
        'concentration_reward': 8,
        'color': (80, 70, 60),  # Dull brown
        'size': 32,
        'shape': 'square',
        'movement': 'straight',
        'armor': 0.5  # Takes 50% damage
    },
    'envy': {
        'name': 'Envy Mara',
        'health': 55,
        'speed': 1.8,
        'merit_reward': 12,  # Increased from 9
        'concentration_reward': 6,
        'color': (100, 180, 80),  # Sickly green
        'size': 18,
        'shape': 'elongated',
        'movement': 'serpentine',
        'serpentine_amplitude': 30,
        'serpentine_frequency': 0.03,
        'merit_steal': 10  # Steals merit on breach
    },
    'pride': {
        'name': 'Pride Mara',
        'health': 90,
        'speed': 1.3,
        'merit_reward': 16,  # Increased from 12 - highest reward
        'concentration_reward': 10,
        'color': (160, 100, 180),  # Royal purple
        'size': 28,
        'shape': 'crown',
        'movement': 'arc',
        'arc_curve': 0.02,
        'metta_immune': True  # Immune to Metta conversion (Phase 2)
    },
    # Bosses - join the end of their wave, stats are fixed (no wave scaling)
    'boss_mara_lord': {
        'name': 'MARA LORD',
        'health': 500,
        'speed': 0.6,
        'merit_reward': 50,
        'concentration_reward': 30,
        'color': (150, 0, 0),  # Blood red
        'size': 50,
        'shape': 'crown',
        'movement': 'straight',
        'armor': 0.3,
        'is_boss': True,
        'temple_damage': 40  # A breach hurts far more than a normal Mara
    },
    'boss_mara_tyrant': {
        'name': 'MARA TYRANT',
        'health': 800,
        'speed': 0.7,
        'merit_reward': 80,
        'concentration_reward': 50,
        'color': (100, 0, 100),  # Deep purple
        'size': 60,
        'shape': 'crown',
        'movement': 'arc',
        'arc_curve': 0.01,
        'armor': 0.4,
        'is_boss': True,
        'temple_damage': 50
    }
}

# Boss waves: wave number -> boss type. The final boss is added on the last wave,
# which depends on difficulty (15 to 30 waves)
BOSS_WAVES = {
    10: 'boss_mara_lord'
}
FINAL_BOSS = 'boss_mara_tyrant'

# Wave settings
WAVE_DELAY = 15.0  # Seconds between waves (was 5.0)
ENEMIES_PER_WAVE_BASE = 5
WAVE_DIFFICULTY_MULTIPLIER = 1.2  # Health/count increases per wave

# Enemy paths (grid coordinates) - each starts at a spawn gate and ends next to the temple.
# Only the corners are listed; the tiles in between are filled in by terrain.py
PATHS = [
    [(0, 7), (13, 7)],                          # Left middle - the main road (bosses use this)
    [(0, 4), (7, 4), (7, 7), (13, 7)],          # Left upper
    [(0, 10), (9, 10), (9, 7), (13, 7)],        # Left lower
    [(5, 0), (5, 4), (7, 4), (7, 7), (13, 7)],  # Top left - joins the upper path
    [(10, 0), (10, 3), (12, 3), (12, 7), (13, 7)]  # Top middle
]

# Map modes - Temple Garden uses the paths above, Open Field is the original
# free-roaming map (enemies walk straight from these spawn points to the temple)
MAP_MODES = {
    'garden': 'Temple Garden',
    'open': 'Open Field'
}
DEFAULT_MAP_MODE = 'garden'
OPEN_FIELD_SPAWNS = [(0, 7), (0, 3), (0, 11), (5, 0), (10, 0)]  # First one is the boss spawn

# Terrain colours - temple garden
TERRACE_COLOR = (72, 118, 66)  # Raised grass where towers go
PATH_COLOR = (196, 172, 124)  # Sandy path
CLIFF_COLOR = (112, 88, 62)  # Rocky edge of the terraces
GATE_COLOR = (60, 20, 70)  # Dark Mara gate where enemies appear

# Projectile settings
PROJECTILE_SPEED = 5
PROJECTILE_SIZE = 6

# Particle effects settings
DEATH_PARTICLES = 12  # Number of particles per death
PARTICLE_LIFETIME = 0.5  # Seconds
AURA_SIZE = 15  # Projectile aura radius

# Game states
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_VICTORY = 'victory'
STATE_DEFEAT = 'defeat'

# Wall system - NEW!
WALL_COST_MERIT = 15
WALL_COST_CONCENTRATION = 5
WALL_HEALTH = 100
WALL_COLOR = (120, 100, 80)  # Stone gray-brown
WALL_DAMAGED_COLOR = (80, 60, 50)  # Darker when damaged
WALL_SIZE = TILE_SIZE  # Same as grid tiles

# Wall levels - 'speed' is how fast Mara move while touching the wall (1.0 = full speed),
# 'damage' is health per second the wall burns from each Mara touching it
WALL_LEVELS = {
    1: {'health': 100, 'speed': 0.3, 'damage': 0, 'effect': 'Slows Mara'},
    2: {'health': 150, 'speed': 0.15, 'damage': 8, 'effect': 'Slows x2 + burns Mara',
        'upgrade_merit': 20, 'upgrade_concentration': 10},
    3: {'health': 250, 'speed': 0.0, 'damage': 12, 'effect': 'Blocks + burns Mara',
        'upgrade_merit': 30, 'upgrade_concentration': 15}
}
WALL_MAX_LEVEL = 3
WALL_ATTACK_DAMAGE = 5  # Health per second each Mara knocks off a wall
WALL_BOSS_ATTACK_DAMAGE = 20  # Bosses smash through faster

# Ability objects positions
LOTUS_POND_POS = (2, 12)  # Grid position (in the pond, clear of the lower path)
BUDDHA_STATUE_POS = (17, 2)  # Grid position (TOP RIGHT - moved!)
MONK_POS = (2, 2)  # Grid position (top left)
ABILITY_OBJECT_SIZE = 40  # Size in pixels
