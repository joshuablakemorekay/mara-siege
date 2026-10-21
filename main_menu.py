"""
Main Menu for Mara's Siege
"""
import pygame
from config import *
from difficulty import DIFFICULTIES, DEFAULT_DIFFICULTY
from guides import GameGuide, StrategyGuide

class MainMenu:
    """Main menu with title, instructions, and start button"""
    
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.start_game = False
        self.selected_difficulty = DEFAULT_DIFFICULTY
        self.difficulty_dropdown_open = False  # NEW! Track if dropdown is open
        
        # Guides - NEW!
        self.game_guide = GameGuide(screen)
        self.strategy_guide = StrategyGuide(screen)
        
        # Fonts
        self.font_title = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        
        # Guide buttons - TOP LEFT
        self.game_guide_button = pygame.Rect(20, 20, 200, 50)
        self.strategy_guide_button = pygame.Rect(20, 80, 200, 50)
        
        # Difficulty dropdown button - TOP RIGHT
        self.difficulty_button = pygame.Rect(
            SCREEN_WIDTH - 260,  # Top right with padding
            20,  # Top padding
            250,
            50
        )
        
        # Dropdown options (only shown when open)
        self.difficulty_options = {}
        option_y = self.difficulty_button.bottom
        for i, key in enumerate(['easy', 'normal', 'hard', 'extreme']):
            self.difficulty_options[key] = pygame.Rect(
                self.difficulty_button.x,
                option_y + i * 45,
                250,
                45
            )
        
        # Start button - Bottom Left
        self.start_button = pygame.Rect(
            50,  # Left side with padding
            SCREEN_HEIGHT - 100,  # Bottom with padding
            250,  # Slightly smaller width
            60
        )

        # Map mode button - next to Start, click to switch maps
        self.selected_map_mode = DEFAULT_MAP_MODE
        self.map_button = pygame.Rect(320, SCREEN_HEIGHT - 100, 250, 60)

    def handle_events(self):
        """Handle menu events"""
        # Check if guide is showing - let guide handle events
        if self.game_guide.showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.game_guide.handle_events(event)
            return
        
        if self.strategy_guide.showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.strategy_guide.handle_events(event)
            return
        
        # Normal menu events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.start_game = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check guide buttons FIRST
                    if self.game_guide_button.collidepoint(event.pos):
                        self.game_guide.showing = True
                        self.game_guide.current_page = 0
                        return
                    
                    if self.strategy_guide_button.collidepoint(event.pos):
                        self.strategy_guide.showing = True
                        self.strategy_guide.current_page = 0
                        return
                    
                    # Check difficulty button (toggle dropdown)
                    if self.difficulty_button.collidepoint(event.pos):
                        self.difficulty_dropdown_open = not self.difficulty_dropdown_open
                        return
                    
                    # Check dropdown options (if open)
                    if self.difficulty_dropdown_open:
                        for key, option_rect in self.difficulty_options.items():
                            if option_rect.collidepoint(event.pos):
                                self.selected_difficulty = key
                                self.difficulty_dropdown_open = False  # Close after selection
                                return
                    
                    # If clicked elsewhere, close dropdown
                    if self.difficulty_dropdown_open:
                        self.difficulty_dropdown_open = False
                    
                    # Map button cycles through the map modes
                    if self.map_button.collidepoint(event.pos):
                        modes = list(MAP_MODES)
                        next_index = (modes.index(self.selected_map_mode) + 1) % len(modes)
                        self.selected_map_mode = modes[next_index]
                        return

                    # Check start button
                    if self.start_button.collidepoint(event.pos):
                        self.start_game = True
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.start_game = True
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.start_game = False
    
    def draw(self):
        """Draw the main menu"""
        # Background
        self.screen.fill(BACKGROUND)
        
        # Draw guide buttons - TOP LEFT
        self.draw_guide_buttons()
        
        # Title
        title = self.font_title.render("Mara's Siege", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Buddhist Tower Defense", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions - Left Column
        y_start = 200
        x_left = 150
        
        instructions_title = self.font_large.render("Controls:", True, GOLD)
        self.screen.blit(instructions_title, (x_left, y_start))
        
        controls = [
            "",
            "Building:",
            "  • Left Click - Place tower/wall or select tower",
            "  • Right Click - Upgrade selected tower",
            "  • 1/2/3 Keys - Select tower type",
            "  • W Key - Toggle wall building mode",
            "  • S Key - Sell tower/wall under mouse",
            "",
            "Combat:",
            "  • SPACE - Start wave (or skip countdown)",
            "  • M Key - Mute / unmute sound",
            "  • ESC - Quit game"
        ]
        
        y_offset = y_start + 40
        for line in controls:
            if line.startswith("  •"):
                text = self.font_small.render(line, True, TEXT_COLOR)
            elif line and not line.startswith(" "):
                text = self.font_medium.render(line, True, ORANGE)
            else:
                text = self.font_small.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (x_left, y_offset))
            y_offset += 25
        
        # Game Info - Right Column
        x_right = 550
        y_start_right = 200
        
        info_title = self.font_large.render("Objective:", True, GOLD)
        self.screen.blit(info_title, (x_right, y_start_right))
        
        objectives = [
            "",
            "Defend the temple from",
            "waves of Mara invaders!",
            "",
            "• Build towers to attack",
            "• Build walls to block paths",
            "• Upgrade for more power",
            "• Survive 20 waves",
            "",
            "Resources:",
            "  Merit (M) - From enemy kills",
            "  Concentration (C) - From waves",
            "  Mindfulness (F) - From perfection"
        ]
        
        y_offset_right = y_start_right + 40
        for line in objectives:
            if line.startswith("•"):
                text = self.font_small.render(line, True, TEXT_COLOR)
            elif line.startswith("  "):
                text = self.font_small.render(line, True, (150, 150, 150))
            elif line and not line.startswith(" "):
                text = self.font_medium.render(line, True, ORANGE)
            else:
                text = self.font_small.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (x_right, y_offset_right))
            y_offset_right += 25
        
        # Difficulty Dropdown - TOP RIGHT
        mouse_pos = pygame.mouse.get_pos()
        current_diff = DIFFICULTIES[self.selected_difficulty]
        
        # Main difficulty button
        is_hovered = self.difficulty_button.collidepoint(mouse_pos)
        if is_hovered or self.difficulty_dropdown_open:
            button_color = (70, 100, 70)
            border_color = GOLD
        else:
            button_color = (50, 80, 50)
            border_color = (120, 120, 120)
        
        pygame.draw.rect(self.screen, button_color, self.difficulty_button)
        pygame.draw.rect(self.screen, border_color, self.difficulty_button, 2)
        
        # Button text
        diff_label = self.font_small.render("DIFFICULTY:", True, (180, 180, 180))
        self.screen.blit(diff_label, (self.difficulty_button.x + 10, self.difficulty_button.y + 8))
        
        diff_name = self.font_medium.render(current_diff['name'], True, current_diff['color'])
        self.screen.blit(diff_name, (self.difficulty_button.x + 10, self.difficulty_button.y + 25))
        
        # Dropdown arrow
        arrow = "▼" if not self.difficulty_dropdown_open else "▲"
        arrow_text = self.font_medium.render(arrow, True, TEXT_COLOR)
        self.screen.blit(arrow_text, (self.difficulty_button.right - 30, self.difficulty_button.y + 12))
        
        # Dropdown options (if open)
        if self.difficulty_dropdown_open:
            for key, option_rect in self.difficulty_options.items():
                diff = DIFFICULTIES[key]
                is_selected = (key == self.selected_difficulty)
                is_option_hovered = option_rect.collidepoint(mouse_pos)
                
                # Option background
                if is_option_hovered:
                    option_color = (70, 100, 70)
                elif is_selected:
                    option_color = (60, 90, 60)
                else:
                    option_color = (45, 70, 45)
                
                pygame.draw.rect(self.screen, option_color, option_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), option_rect, 1)
                
                # Option text
                option_text = self.font_small.render(diff['name'], True, diff['color'])
                waves_text = self.font_small.render(f"({diff['waves']} waves)", True, (150, 150, 150))
                
                self.screen.blit(option_text, (option_rect.x + 10, option_rect.y + 5))
                self.screen.blit(waves_text, (option_rect.x + 10, option_rect.y + 23))
        
        # Start Button
        if self.start_button.collidepoint(mouse_pos):
            button_color = (80, 150, 80)
            border_color = GOLD
        else:
            button_color = (50, 100, 50)
            border_color = (100, 150, 100)
        
        pygame.draw.rect(self.screen, button_color, self.start_button)
        pygame.draw.rect(self.screen, border_color, self.start_button, 3)
        
        button_text = self.font_large.render("START GAME", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=self.start_button.center)
        self.screen.blit(button_text, button_text_rect)

        # Map button - shows the chosen map, click to switch
        is_hovered = self.map_button.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (70, 110, 70) if is_hovered else (50, 90, 50), self.map_button)
        pygame.draw.rect(self.screen, GOLD if is_hovered else (120, 150, 120), self.map_button, 2)
        map_label = self.font_small.render("MAP (click to change):", True, (200, 200, 200))
        self.screen.blit(map_label, (self.map_button.x + 10, self.map_button.y + 8))
        map_name = self.font_medium.render(MAP_MODES[self.selected_map_mode], True, GOLD)
        self.screen.blit(map_name, (self.map_button.x + 10, self.map_button.y + 32))
        
        # Footer hint - Bottom Right (to balance button on left)
        hint = self.font_small.render("Press ENTER or SPACE to start", True, (120, 120, 120))
        hint_rect = hint.get_rect(bottomright=(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30))
        self.screen.blit(hint, hint_rect)
        
        # Draw guides if showing (AFTER everything else)
        self.game_guide.draw()
        self.strategy_guide.draw()
    
    def draw_guide_buttons(self):
        """Draw game guide and strategy guide buttons"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Game Guide button
        is_hovered = self.game_guide_button.collidepoint(mouse_pos)
        color = (70, 110, 70) if is_hovered else (50, 90, 50)
        border = GOLD if is_hovered else (120, 150, 120)
        
        pygame.draw.rect(self.screen, color, self.game_guide_button)
        pygame.draw.rect(self.screen, border, self.game_guide_button, 2)
        
        text = self.font_medium.render("📖 GAME GUIDE", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.game_guide_button.center)
        self.screen.blit(text, text_rect)
        
        # Strategy Guide button
        is_hovered2 = self.strategy_guide_button.collidepoint(mouse_pos)
        color2 = (70, 110, 70) if is_hovered2 else (50, 90, 50)
        border2 = GOLD if is_hovered2 else (120, 150, 120)
        
        pygame.draw.rect(self.screen, color2, self.strategy_guide_button)
        pygame.draw.rect(self.screen, border2, self.strategy_guide_button, 2)
        
        text2 = self.font_medium.render("⚔️ STRATEGY", True, (255, 255, 255))
        text2_rect = text2.get_rect(center=self.strategy_guide_button.center)
        self.screen.blit(text2, text2_rect)
    
    def run(self):
        """Run the main menu loop"""
        clock = pygame.time.Clock()
        
        while self.running and not self.start_game:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        
        return (self.start_game, self.selected_difficulty, self.selected_map_mode)
