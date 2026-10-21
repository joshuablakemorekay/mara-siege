"""
In-game guide system for Mara's Siege
"""
import pygame
from config import *

class GameGuide:
    """Comprehensive game guide with all features documented"""
    
    def __init__(self, screen):
        self.screen = screen
        self.showing = False
        self.current_page = 0
        self.font_title = pygame.font.Font(None, 48)
        self.font_header = pygame.font.Font(None, 32)
        self.font_text = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Define all guide pages
        self.pages = self.create_guide_pages()
        self.max_page = len(self.pages) - 1
    
    def create_guide_pages(self):
        """Create all guide content"""
        return [
            # Page 0: Overview
            {
                'title': 'Game Overview',
                'content': [
                    ('OBJECTIVE', 'header'),
                    ('Defend the Buddhist temple from waves of Mara invaders', 'text'),
                    ('Survive 20 waves (or more on harder difficulties)', 'text'),
                    ('', 'space'),
                    ('BASIC GAMEPLAY', 'header'),
                    ('• Build towers to attack enemies', 'text'),
                    ('• Build walls to block and redirect paths', 'text'),
                    ('• Manage 3 resources: Merit, Concentration, Mindfulness', 'text'),
                    ('• Use 3 special abilities strategically (3 uses each)', 'text'),
                    ('• Upgrade towers for more power', 'text'),
                    ('', 'space'),
                    ('LOSE CONDITIONS', 'header'),
                    ('• Temple reaches 0 HP', 'text'),
                    ('• Each enemy breach deals 10 damage', 'text'),
                ]
            },
            # Page 1: Controls
            {
                'title': 'Controls',
                'content': [
                    ('BUILDING', 'header'),
                    ('• Left Click: Place tower/wall or select tower', 'text'),
                    ('• Right Click: Upgrade selected tower', 'text'),
                    ('• 1/2/3 Keys: Select tower type (Sati/Viriya/Samadhi)', 'text'),
                    ('• W Key: Toggle wall building mode', 'text'),
                    ('• ESC or X: Clear cursor (remove preview)', 'text'),
                    ('', 'space'),
                    ('COMBAT', 'header'),
                    ('• SPACE: Start wave (or skip countdown)', 'text'),
                    ('', 'space'),
                    ('ABILITIES', 'header'),
                    ('• Click Lotus Pond (bottom left): Metta Healing', 'text'),
                    ('• Click Buddha Statue (top right): Samadhi Wave', 'text'),
                    ('• Click Monk (top left): Karuna Strike', 'text'),
                ]
            },
            # Page 2: Resources
            {
                'title': 'Resources',
                'content': [
                    ('MERIT (M) - Gold', 'header'),
                    ('• Gained: Killing enemies', 'text'),
                    ('• Used: Building towers, walls, Metta/Karuna abilities', 'text'),
                    ('• Starting: 80-150 (depends on difficulty)', 'text'),
                    ('', 'space'),
                    ('CONCENTRATION (C) - Orange', 'header'),
                    ('• Gained: Killing enemies + wave completion', 'text'),
                    ('• Used: Building Samadhi towers, Samadhi/Karuna abilities', 'text'),
                    ('• Starting: 25-50 (depends on difficulty)', 'text'),
                    ('', 'space'),
                    ('MINDFULNESS (F) - Blue', 'header'),
                    ('• Gained: Passive regen (0.5/sec), perfect waves', 'text'),
                    ('• Used: Building Sati towers, Metta/Samadhi abilities', 'text'),
                    ('• Starting: 15-40 (depends on difficulty)', 'text'),
                ]
            },
            # Page 3: Towers
            {
                'title': 'Towers',
                'content': [
                    ('SATI TOWER (Mindfulness) - Blue', 'header'),
                    ('• Cost: 30M + 15F', 'text'),
                    ('• Damage: 8 → 12 → 16 (with upgrades)', 'text'),
                    ('• Range: Medium', 'text'),
                    ('• Best vs: Balanced, all enemy types', 'text'),
                    ('', 'space'),
                    ('VIRIYA TOWER (Energy) - Red', 'header'),
                    ('• Cost: 40M', 'text'),
                    ('• Damage: 10 → 15 → 20', 'text'),
                    ('• Range: Long', 'text'),
                    ('• Best vs: Single targets, high HP enemies', 'text'),
                    ('', 'space'),
                    ('SAMADHI TOWER (Concentration) - Purple', 'header'),
                    ('• Cost: 35M + 20C', 'text'),
                    ('• Damage: 6 → 9 → 12', 'text'),
                    ('• Range: Short, attacks multiple enemies', 'text'),
                    ('• Best vs: Swarms of weak enemies', 'text'),
                ]
            },
            # Page 4: Enemies
            {
                'title': 'Enemies (Part 1)',
                'content': [
                    ('DOUBT (Wave 1+) - Gray', 'header'),
                    ('• HP: Low | Speed: Medium | Rewards: 8M, 3C', 'text'),
                    ('• Basic enemy, no special abilities', 'text'),
                    ('', 'space'),
                    ('CRAVING (Wave 2+) - Orange', 'header'),
                    ('• HP: Low | Speed: Fast | Rewards: 6M, 2C', 'text'),
                    ('• Zigzag movement pattern', 'text'),
                    ('', 'space'),
                    ('DELUSION (Wave 3+) - Purple', 'header'),
                    ('• HP: Medium | Speed: Medium | Rewards: 10M, 4C', 'text'),
                    ('• Serpentine movement', 'text'),
                    ('', 'space'),
                    ('ANGER (Wave 9+) - Red', 'header'),
                    ('• HP: Medium | Speed: Fast | Rewards: 11M, 5C', 'text'),
                    ('• Arc movement, damages towers when nearby!', 'text'),
                ]
            },
            # Page 5: More Enemies
            {
                'title': 'Enemies (Part 2)',
                'content': [
                    ('IGNORANCE (Wave 12+) - Dark', 'header'),
                    ('• HP: High | Speed: Slow | Rewards: 14M, 8C', 'text'),
                    ('• 3 armor (reduces damage by 3)', 'text'),
                    ('• Tank enemy, very durable', 'text'),
                    ('', 'space'),
                    ('ENVY (Wave 15+) - Green', 'header'),
                    ('• HP: Medium | Speed: Fast | Rewards: 12M, 6C', 'text'),
                    ('• Steals 5 Merit when reaching temple', 'text'),
                    ('', 'space'),
                    ('PRIDE (Wave 18+) - Gold', 'header'),
                    ('• HP: Very High | Speed: Medium | Rewards: 16M, 10C', 'text'),
                    ('• Boss enemy, immune to Metta healing effect', 'text'),
                    ('• Appears earlier on higher difficulties', 'text'),
                ]
            },
            # Page 6: Abilities
            {
                'title': 'Special Abilities',
                'content': [
                    ('METTA HEALING (Lotus Pond)', 'header'),
                    ('• Cost: 50M + 30F | Cooldown: 30s | Uses: 3/game', 'text'),
                    ('• 1st use: Heal temple +10 HP', 'text'),
                    ('• 2nd use: Heal temple +15 HP', 'text'),
                    ('• 3rd use: Heal temple +25 HP', 'text'),
                    ('• Total: 50 HP healing! Use for emergencies', 'text'),
                    ('', 'space'),
                    ('SAMADHI WAVE (Buddha)', 'header'),
                    ('• Cost: 40C + 40F | Cooldown: 40s | Uses: 3/game', 'text'),
                    ('• Freezes ALL enemies for 5 seconds', 'text'),
                    ('• Towers continue shooting!', 'text'),
                    ('• Best for: Boss waves, overwhelming swarms', 'text'),
                    ('', 'space'),
                    ('KARUNA STRIKE (Monk)', 'header'),
                    ('• Cost: 60M + 50C | Cooldown: 35s | Uses: 3/game', 'text'),
                    ('• Deals 30 damage to ALL enemies on screen', 'text'),
                    ('• Best for: Clearing weak enemies', 'text'),
                ]
            },
            # Page 7: Difficulties
            {
                'title': 'Difficulty Levels',
                'content': [
                    ('EASY - Novice Monk', 'header'),
                    ('• 15 waves | 20s between waves', 'text'),
                    ('• 80% enemy HP/count | 120% rewards', 'text'),
                    ('• Starting: 150M, 50C, 40F', 'text'),
                    ('', 'space'),
                    ('NORMAL - Temple Guardian', 'header'),
                    ('• 20 waves | 15s between waves', 'text'),
                    ('• 100% enemy HP/count | 100% rewards', 'text'),
                    ('• Starting: 120M, 40C, 30F', 'text'),
                    ('', 'space'),
                    ('HARD - Dharma Defender', 'header'),
                    ('• 25 waves | 12s between waves', 'text'),
                    ('• 120% enemy HP, 130% count | 90% rewards', 'text'),
                    ('• Starting: 100M, 30C, 20F', 'text'),
                    ('', 'space'),
                    ('EXTREME - Enlightenment Trial', 'header'),
                    ('• 30 waves | 10s between waves', 'text'),
                    ('• 150% enemy HP, 160% count | 80% rewards', 'text'),
                    ('• Starting: 80M, 25C, 15F | Masters only!', 'text'),
                ]
            },
        ]
    
    def handle_events(self, event):
        """Handle guide input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_g:
                self.showing = False
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.current_page = max(0, self.current_page - 1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.current_page = min(self.max_page, self.current_page + 1)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check navigation buttons
            if 50 < mouse_x < 150 and SCREEN_HEIGHT - 80 < mouse_y < SCREEN_HEIGHT - 40:
                self.current_page = max(0, self.current_page - 1)
            elif 170 < mouse_x < 270 and SCREEN_HEIGHT - 80 < mouse_y < SCREEN_HEIGHT - 40:
                self.current_page = min(self.max_page, self.current_page + 1)
            elif SCREEN_WIDTH - 150 < mouse_x < SCREEN_WIDTH - 50 and SCREEN_HEIGHT - 80 < mouse_y < SCREEN_HEIGHT - 40:
                self.showing = False
    
    def draw(self):
        """Draw the guide"""
        if not self.showing:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((20, 30, 25))
        self.screen.blit(overlay, (0, 0))
        
        # Draw current page
        page = self.pages[self.current_page]
        
        # Title
        title = self.font_title.render(page['title'], True, GOLD)
        self.screen.blit(title, (50, 30))
        
        # Content
        y_offset = 100
        for line, style in page['content']:
            if style == 'header':
                text = self.font_header.render(line, True, ORANGE)
                y_offset += 10
            elif style == 'text':
                text = self.font_text.render(line, True, (220, 220, 220))
            elif style == 'space':
                y_offset += 15
                continue
            
            self.screen.blit(text, (60, y_offset))
            y_offset += 28 if style == 'header' else 24
        
        # Page indicator
        page_text = self.font_text.render(f"Page {self.current_page + 1} / {self.max_page + 1}", True, (180, 180, 180))
        self.screen.blit(page_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100))
        
        # Navigation buttons
        self.draw_button("< PREV", 50, SCREEN_HEIGHT - 80, 100, 40, self.current_page > 0)
        self.draw_button("NEXT >", 170, SCREEN_HEIGHT - 80, 100, 40, self.current_page < self.max_page)
        self.draw_button("CLOSE", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 100, 40, True)
        
        # Controls hint
        hint = self.font_small.render("Arrow keys or A/D to navigate | ESC or G to close", True, (150, 150, 150))
        self.screen.blit(hint, (50, SCREEN_HEIGHT - 25))
    
    def draw_button(self, text, x, y, w, h, enabled):
        """Draw a button"""
        color = (60, 100, 60) if enabled else (40, 40, 40)
        border = (200, 200, 100) if enabled else (100, 100, 100)
        
        button_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, border, button_rect, 2)
        
        button_text = self.font_text.render(text, True, (255, 255, 255) if enabled else (120, 120, 120))
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)


class StrategyGuide:
    """Strategy guide with advanced tactics"""
    
    def __init__(self, screen):
        self.screen = screen
        self.showing = False
        self.current_page = 0
        self.font_title = pygame.font.Font(None, 48)
        self.font_header = pygame.font.Font(None, 32)
        self.font_text = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        self.pages = self.create_strategy_pages()
        self.max_page = len(self.pages) - 1
    
    def create_strategy_pages(self):
        """Create strategy content"""
        return [
            # Page 0: Early Game
            {
                'title': 'Early Game Strategy (Waves 1-7)',
                'content': [
                    ('OPENING BUILD', 'header'),
                    ('• Start: Place 2 Viriya towers near temple entrance', 'text'),
                    ('• Cost: 80M (leaves 40M+)', 'text'),
                    ('• Why: Long range, good damage, covers early waves', 'text'),
                    ('', 'space'),
                    ('WALL PLACEMENT', 'header'),
                    ('• Waves 2-3: Build 2-3 walls to create funnel', 'text'),
                    ('• Force enemies through tower overlapping fire', 'text'),
                    ('• Cost: 15M + 5C each (cheap!)', 'text'),
                    ('', 'space'),
                    ('RESOURCE MANAGEMENT', 'header'),
                    ('• Save Mindfulness for Sati tower (Wave 5-6)', 'text'),
                    ('• Build Samadhi when Concentration reaches 55M+20C', 'text'),
                    ('• Dont upgrade yet - spread coverage first', 'text'),
                ]
            },
            # Page 1: Mid Game
            {
                'title': 'Mid Game Strategy (Waves 8-15)',
                'content': [
                    ('TOWER MIX', 'header'),
                    ('• 3-4 Viriya (damage dealers)', 'text'),
                    ('• 2-3 Samadhi (swarm control)', 'text'),
                    ('• 1-2 Sati (balanced support)', 'text'),
                    ('', 'space'),
                    ('UPGRADE PRIORITY', 'header'),
                    ('• Level 2: Viriya towers near entrance (focus fire)', 'text'),
                    ('• Level 2: Samadhi towers at choke points', 'text'),
                    ('• Save Level 3 for late game', 'text'),
                    ('', 'space'),
                    ('ABILITY USAGE', 'header'),
                    ('• Wave 8-10: Use Karuna #1 on first swarm', 'text'),
                    ('• Wave 12: Use Samadhi #1 if overwhelmed', 'text'),
                    ('• Save Metta unless temple below 70 HP', 'text'),
                ]
            },
            # Page 2: Late Game
            {
                'title': 'Late Game Strategy (Waves 16-20)',
                'content': [
                    ('FINAL DEFENSE', 'header'),
                    ('• Upgrade key towers to Level 3', 'text'),
                    ('• Add 1-2 more Samadhi for swarm waves', 'text'),
                    ('• Extend wall maze if resources allow', 'text'),
                    ('', 'space'),
                    ('BOSS WAVES', 'header'),
                    ('• Wave 10: Mara Lord • Final wave: Mara Tyrant', 'text'),
                    ('• Focus fire: All Viriya towers target boss', 'text'),
                    ('• Use Samadhi Wave to freeze + burst damage', 'text'),
                    ('', 'space'),
                    ('FINAL WAVE (20)', 'header'),
                    ('• Use ALL remaining abilities', 'text'),
                    ('• Combo: Samadhi freeze → Karuna strike → Metta heal', 'text'),
                    ('• No tomorrow - empty your arsenal!', 'text'),
                ]
            },
            # Page 3: Tower Positioning
            {
                'title': 'Tower Positioning',
                'content': [
                    ('VIRIYA PLACEMENT', 'header'),
                    ('• Near temple: Last line of defense', 'text'),
                    ('• Long range = position anywhere with line of sight', 'text'),
                    ('• Upgrade these FIRST (highest DPS)', 'text'),
                    ('', 'space'),
                    ('SAMADHI PLACEMENT', 'header'),
                    ('• At choke points where enemies cluster', 'text'),
                    ('• Behind walls in funnel areas', 'text'),
                    ('• Multi-hit = maximum value with groups', 'text'),
                    ('', 'space'),
                    ('SATI PLACEMENT', 'header'),
                    ('• Flexible - fill gaps in coverage', 'text'),
                    ('• Medium range = midfield positioning', 'text'),
                    ('• Balanced damage = reliable anywhere', 'text'),
                ]
            },
            # Page 4: AI Behavior
            {
                'title': 'Enemy AI Mechanics',
                'content': [
                    ('PATHFINDING', 'header'),
                    ('• Enemies path directly to temple', 'text'),
                    ('• Walls force recalculation - enemies go around', 'text'),
                    ('• Create mazes to maximize path length', 'text'),
                    ('', 'space'),
                    ('ATTACK PRIORITY', 'header'),
                    ('• Towers: Attack nearest enemy in range', 'text'),
                    ('• No target switching - finish kill first', 'text'),
                    ('• Multi-hit towers damage 2-3 enemies per shot', 'text'),
                    ('', 'space'),
                    ('SPECIAL BEHAVIORS', 'header'),
                    ('• Anger: Damages towers when within 30 pixels', 'text'),
                    ('• Envy: Steals Merit on temple breach', 'text'),
                    ('• Ignorance: Armor absorbs 3 damage per hit', 'text'),
                    ('• Walls: Enemies attack if blocking path (5 dmg/sec)', 'text'),
                ]
            },
            # Page 5: Advanced Tactics
            {
                'title': 'Advanced Tactics',
                'content': [
                    ('MAZE STRATEGY', 'header'),
                    ('• Build walls in S-pattern to maximize path', 'text'),
                    ('• More path length = more tower shots per enemy', 'text'),
                    ('• Example: 3-wall maze = 2x path length', 'text'),
                    ('', 'space'),
                    ('ABILITY COMBOS', 'header'),
                    ('• Freeze + Strike: Samadhi → Karuna = massive clear', 'text'),
                    ('• Strike + Heal: Karuna → Metta = aggressive defense', 'text'),
                    ('• Save 3rd uses: Final wave = all 3 abilities', 'text'),
                    ('', 'space'),
                    ('RESOURCE TRICKS', 'header'),
                    ('• Perfect waves: +Mindfulness bonus (0 breaches)', 'text'),
                    ('• Wave skip: Press SPACE early = faster farming', 'text'),
                    ('• Tower selling: Not available - plan carefully!', 'text'),
                ]
            },
        ]
    
    def handle_events(self, event):
        """Handle strategy guide input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_s:
                self.showing = False
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.current_page = max(0, self.current_page - 1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.current_page = min(self.max_page, self.current_page + 1)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if 50 < mouse_x < 150 and SCREEN_HEIGHT - 80 < mouse_y < SCREEN_HEIGHT - 40:
                self.current_page = max(0, self.current_page - 1)
            elif 170 < mouse_x < 270 and SCREEN_HEIGHT - 80 < mouse_y < SCREEN_HEIGHT - 40:
                self.current_page = min(self.max_page, self.current_page + 1)
            elif SCREEN_WIDTH - 150 < mouse_x < SCREEN_WIDTH - 50 and SCREEN_HEIGHT - 80 < mouse_y < SCREEN_HEIGHT - 40:
                self.showing = False
    
    def draw(self):
        """Draw the strategy guide (same rendering as game guide)"""
        if not self.showing:
            return
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((25, 30, 20))
        self.screen.blit(overlay, (0, 0))
        
        page = self.pages[self.current_page]
        
        title = self.font_title.render(page['title'], True, GOLD)
        self.screen.blit(title, (50, 30))
        
        y_offset = 100
        for line, style in page['content']:
            if style == 'header':
                text = self.font_header.render(line, True, ORANGE)
                y_offset += 10
            elif style == 'text':
                text = self.font_text.render(line, True, (220, 220, 220))
            elif style == 'space':
                y_offset += 15
                continue
            
            self.screen.blit(text, (60, y_offset))
            y_offset += 28 if style == 'header' else 24
        
        page_text = self.font_text.render(f"Page {self.current_page + 1} / {self.max_page + 1}", True, (180, 180, 180))
        self.screen.blit(page_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100))
        
        self.draw_button("< PREV", 50, SCREEN_HEIGHT - 80, 100, 40, self.current_page > 0)
        self.draw_button("NEXT >", 170, SCREEN_HEIGHT - 80, 100, 40, self.current_page < self.max_page)
        self.draw_button("CLOSE", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 100, 40, True)
        
        hint = self.font_small.render("Arrow keys or A/D to navigate | ESC or S to close", True, (150, 150, 150))
        self.screen.blit(hint, (50, SCREEN_HEIGHT - 25))
    
    def draw_button(self, text, x, y, w, h, enabled):
        """Draw a button"""
        color = (60, 100, 60) if enabled else (40, 40, 40)
        border = (200, 200, 100) if enabled else (100, 100, 100)
        
        button_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, border, button_rect, 2)
        
        button_text = self.font_text.render(text, True, (255, 255, 255) if enabled else (120, 120, 120))
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)
