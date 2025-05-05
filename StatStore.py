import pygame
import random
import UserInterface as ui

not_enough_sound = pygame.mixer.Sound('Sounds/synth.wav')

class StatShop():
    def __init__(self, player):
        display = pygame.display.get_surface()
        self.player = player
        self.font = pygame.font.Font('Assets/Font/VT323-Regular.ttf', size=30)
        self.top_text = self.font.render('Choose a skill', False, 'White')
        self.font.set_underline(True)
        self.local_position = pygame.math.Vector2(0, 0)
        self.closed = False
        
        
        w, h = display.get_width(), display.get_height()
        self.screen_overlay = pygame.Rect(self.local_position.x, self.local_position.y, w, h)
        
        self.stats = {
            'Hard Noggin' : {
                'Icon' : 'Assets/Stats/Hard Noggin.png',
                'Description' : 'Decreases damage taken.',
                'Price' : 5
            },
            'Pocket Bullets' : {
                'Icon' : 'Assets/Stats/Pocket Bullets.png',
                'Description' : 'Makes you shoot excessive bullets.',
                'Price' : 5
            },
            'Trigger Happy' : {
                'Icon' : 'Assets/Stats/Trigger Happy.png',
                'Description' : 'Increases fire rate.',
                'Price' : 5
            },
            'Juice Up' : {
                'Icon' : 'Assets/Stats/Juice Up.png',
                'Description' : 'Increases max HP.',
                'Price' : 5
            },
            'Accurate' : {
                'Icon' : 'Assets/Stats/Accurate.png',
                'Description' : 'Increases accuracy',
                'Price' : 5
            },
        }
        
        self.selected_stats = {
            1 : None,
            2 : None
        }
        
        self.randomize_selected()
        self.button_one = ui.TextureButton(self.local_position + (220, 195), self.selected_stats[1]['Icon'], lambda: self.purchase_stat(1), 5)
        self.button_two = ui.TextureButton(self.local_position + (470, 195), self.selected_stats[2]['Icon'], lambda: self.purchase_stat(2), 5)
        self.close_button = ui.TextureButton(self.local_position + (800, 30), 'Assets/UI/x button.png', self.close_shop, 5)
        self.reroll_button = ui.Button(self.local_position.x + 600, self.local_position.y + 550, 200, 65, self.reroll, 'grey', 'Re-Roll! x5')
        
        self.stat_one_price = self.font.render(f"x{self.selected_stats[1]['Price']}", False, 'White')
        self.stat_two_price = self.font.render(f"x{self.selected_stats[2]['Price']}", False, 'White')
        self.reroll_price = 5
        self.description = self.font.render('Test Description', False, 'White')
    
    
    def purchase_stat(self, button):
        # Check if the player has enough souls
        if self.selected_stats[button]['Price'] > self.player.souls:
            not_enough_sound.play()
            return
    
        # Deduct the price from the player's souls
        self.player.souls -= self.selected_stats[button]['Price']
    
        # Increase the price for the next purchase
        self.selected_stats[button]['Price'] += 3
    
        # Find the correct stat key and update the player's stats
        for key, value in self.stats.items():
            if value == self.selected_stats[button]:  # Match the selected stat
                if key == 'Trigger Happy' or key == 'Juice Up':
                    self.player.stats[key] += random.randrange(5, 15)
                elif key == 'Hard Noggin' or key == 'Accurate':
                    self.player.stats[key] += random.randrange(1, 5)
                elif key == 'Pocket Bullets':
                    self.player.stats[key] += 1
                break  # Exit the loop once the stat is updated
    
        self.close_shop()
    
    
    def reroll(self):
        if self.player.souls < self.reroll_price:
            not_enough_sound.play()
            return
        self.player.souls -= self.reroll_price
        self.reroll_price += 5
        self.randomize_selected()
        self.reroll_button = ui.Button(self.local_position.x + 600, self.local_position.y + 550, 200, 65, self.reroll, 'grey', f'Re-Roll! x{self.reroll_price}')
    
    
    def close_shop(self):
        self.closed = True
    
    
    def update(self):
        self.button_one.update()
        self.button_two.update()
        self.reroll_button.update()
        self.close_button.update()
        
        if self.button_one.hovering:
            self.description = self.font.render(self.selected_stats[1]['Description'], False, 'White')
        elif self.button_two.hovering:
            self.description = self.font.render(self.selected_stats[2]['Description'], False, 'White')
            
        
    
    def draw(self):
        surface = pygame.display.get_surface()
        
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((114, 114, 114, 200))  # White with 200 alpha

        # Blit the transparent surface onto the main surface
        surface.blit(overlay, self.screen_overlay.topleft)
        
        self.stat_one_price = self.font.render(f"x{self.selected_stats[1]['Price']}", False, 'White')
        self.stat_two_price = self.font.render(f"x{self.selected_stats[2]['Price']}", False, 'White')
        
        surface.blit(self.top_text, (325, 20))
        surface.blit(self.stat_one_price, (285, 100))
        surface.blit(self.stat_two_price, (550, 100))
        
        self.button_one.draw()
        self.button_two.draw()
        self.close_button.draw()
        self.reroll_button.draw()
        
        if self.button_one.hovering or self.button_two.hovering:
            surface.blit(self.description, (325, 400))
        
    
    def randomize_selected(self):
        stats = self.stats.copy()

        # Randomly select a stat
        self.selected_stats[1] = random.choice(list(stats.values()))

        # Find the key in self.stats that matches the selected stat
        for key, value in list(stats.items()):
            if value == self.selected_stats[1]:
                del stats[key] # Delete selected stat so it cant be chosen again
                break
        
        self.selected_stats[2] = random.choice(list(stats.values()))
        
        self.button_one = ui.TextureButton(self.local_position + (220, 195), self.selected_stats[1]['Icon'], lambda: self.purchase_stat(1), 5)
        self.button_two = ui.TextureButton(self.local_position + (470, 195), self.selected_stats[2]['Icon'], lambda: self.purchase_stat(2), 5)