# Mara's Siege - Buddhist Tower Defense Game

A strategic tower defense game where you defend the temple of the mind against waves of Mara invaders while striving toward enlightenment.

## Concept

You enter the mind of a meditator in deep meditation, being attacked by evil Mara (Buddhist concept of temptation/delusion). Use Buddhist mental qualities as strategic defenses to protect the temple and achieve enlightenment.

## How to Play

### Objective
- **Victory**: Survive 20 waves AND accumulate 1000 Merit
- **Defeat**: Temple health reaches 0 OR 10+ breaches occur

### Resources (V4 NEW SYSTEM!)
- **Merit (M)** - Gold: From killing enemies, builds Viriya towers
- **Concentration (C)** - Orange: From wave completion, builds Samadhi towers  
- **Mindfulness (F)** - Blue: From perfect waves + regen, builds Sati towers

### Controls (V4 SIMPLIFIED!)
- **Left Click**: Place tower OR Select existing tower
- **Right Click**: Upgrade selected tower (instant!)
- **1/2/3 Keys**: Quick-select tower type
- **SPACE**: Start next wave
- **ESC**: Quit game

### Tower Types (Buddhist Mental Qualities)

#### Viriya Tower (Energy) - 40 Merit
- Fast attack rate, moderate damage
- **Cost**: 40M (Merit only - most accessible!)
- **Upgradeable**: +5 damage, +15 range per level
- Color: Orange

#### Samadhi Tower (Concentration) - 35M + 20C
- Slow attack, very high damage
- **Cost**: 35 Merit + 20 Concentration
- **Upgradeable**: +20 damage, +25 range per level
- Color: Purple

#### Sati Tower (Mindfulness) - 30M + 15F
- Balanced stats, good all-around
- **Cost**: 30 Merit + 15 Mindfulness
- **Upgradeable**: +8 damage, +20 range per level
- Color: Light Blue

### Enemy Types (Mara Manifestations)

**7 unique enemy types with different shapes, sizes, and behaviors!**

#### Basic Enemies (Waves 1-5)
- **Doubt Mara** ⚫ - Slow circle, moderate health
- **Craving Mara** ⚫ - Fast circle, low health

#### Intermediate (Waves 6-11)
- **Delusion Mara** 🫧 - Large blob, **zig-zag movement**
- **Anger Mara** 🔺 - Triangle, very fast, **damages towers**

#### Advanced (Waves 12-17)
- **Ignorance Mara** ⬛ - Large square, **50% armor**
- **Envy Mara** 📏 - Elongated, **serpentine movement**, **steals Merit**

#### Elite (Waves 18-20)
- **Pride Mara** 👑 - Crown shape, **arc movement**, elite stats

**See [ENEMY_GUIDE.md](ENEMY_GUIDE.md) for complete enemy strategies!**

### Visual Effects (NEW!)
- **Death Explosions**: Enemies burst into particles when defeated
- **Projectile Auras**: Pulsing colored auras based on tower type
  - Blue: Mindfulness (Sati)
  - Orange: Energy (Viriya)
  - Purple: Concentration (Samadhi)
- **Meditation Garden**: Lotus pond, Buddha statue, monks in orange robes

## Installation & Running

### Requirements
```bash
python 3.7+
pygame
```

### Install Dependencies
```bash
pip install pygame
```

### Run the Game
```bash
cd mara_siege
python main.py
```

## Game Mechanics

### Wave System
- 20 total waves to complete
- Enemies spawn in increasing numbers
- Health scales with wave number
- 5-second delay between waves

### Placement Strategy
- Towers can be placed anywhere except:
  - On the temple
  - On existing towers
  - Outside the grid
- Plan strategic chokepoints
- Use range circles to optimize coverage

### Resource Economy
- Earn Merit by defeating enemies
- Each enemy type gives different Merit rewards
- Manage spending vs. saving for stronger towers

## File Structure
```
mara_siege/
├── main.py              # Main game loop (500+ lines)
├── config.py            # Game constants
├── resource_manager.py  # Resource tracking
├── temple.py            # Temple/central structure
├── tower.py             # Tower classes with upgrades
├── enemy.py             # Enemy classes with labels
├── projectile.py        # Projectile attacks with auras
├── wave_manager.py      # Wave spawning logic
├── particles.py         # Particle system for effects
├── README.md            # This file
└── CHANGELOG.md         # Version history
```

## Future Phases (Planned)

### Phase 2: Advanced Buddhist Abilities
- **Metta Towers**: Convert enemies to allies
- **Karuna Towers**: Heal damaged structures
- **Panna Towers**: Area damage with wisdom

### Phase 3: Enhanced Gameplay
- More enemy types (Anger, Delusion, Pride, Restlessness)
- Boss waves (Mara King)
- Upgradable towers
- Special abilities using Concentration/Mindfulness

### Phase 4: Polish & Content
- Save/load system
- Achievement system
- Better graphics/sprites
- Sound effects and music
- Difficulty modes

## Development Notes

**Built with**: Python + Pygame  
**Theme**: Buddhist meditation and mental cultivation  
**Genre**: 2D Tower Defense  
**Version**: 3.0 - Enemy Variety Update  
**Status**: Phase 1 Complete - 7 Unique Enemies!

## What's New in V3

✨ **7 Enemy Types** - Diverse Mara manifestations  
✨ **Unique Shapes** - Circle, Triangle, Square, Blob, Elongated, Crown  
✨ **Movement Patterns** - Straight, Zig-Zag, Serpentine, Arc  
✨ **Special Abilities** - Armor, Tower Damage, Merit Steal  
✨ **Progressive Waves** - New enemies introduced gradually  
✨ **Strategic Depth** - Each enemy requires different counter-strategy

## Credits

**Game Design**: Joshua  
**Buddhist Concepts**: Traditional Theravada Buddhism  
**Development**: Learning project combining game dev with dharma practice

---

*"Just as a solid rock is not shaken by the storm, even so the wise are not affected by praise or blame." - Dhammapada*
