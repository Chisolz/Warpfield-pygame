import pygame
import json
import os
import math
import random
from UserInterface import PickupUI

class Item:
    def __init__(self, position, tipe):
        self.scale = 3
        self.in_contact = False
        self.equipped = False
        self.display = pygame.display.get_surface()
        self.position = position
        self.type = tipe
        self.rect = pygame.Rect(position.x, position.y, 50, 50)
        self.float_offset = 0
        self.float_timer = 0
        self.time_placed = pygame.time.get_ticks()
        self.despawn_time = 15000
    

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        self.float_timer += dt * 3
        self.float_offset = math.sin(self.float_timer) * 7
        
        if current_time - self.time_placed >= self.despawn_time:
            self.equipped = True
        

    def draw(self):
        pass



class Gun(Item):
    def __init__(self, position, gunName):
        super().__init__(position, 'gun')
        self.name = gunName
        self.sprites = {}
        self.ui = PickupUI(self.position)

        directory = "Assets\Guns"
        gunData = None
        for file in os.listdir(directory):
            if file.endswith(".json"):
                with open(directory+'/'+file) as f:
                    gunData = json.load(f)
                f.close()
            if file.endswith('.png'):
                sprite = pygame.image.load(directory+'/'+file)
                width, height = sprite.get_width(), sprite.get_height()
                spriteScaled = pygame.transform.scale(sprite, (self.scale * width, self.scale * height))
                sprite_name = file.removesuffix('.png')
                self.sprites[sprite_name] = spriteScaled
        
        self.selected_sprite = self.sprites[self.name]
    
    
    def update(self, dt):
        super().update(dt)
        if self.in_contact:
            self.ui.play_anim()
        else:
            self.ui.reset_anim()
    
    
    def draw(self, offset):
        float_position = self.position - offset
        float_position.y += self.float_offset
        self.display.blit(self.selected_sprite, float_position)
        
        if self.in_contact:
            self.ui.draw(float_position)



class HealthDrop(Item):
    def __init__(self, spawnPos):
        super().__init__(spawnPos, 'health')
        sprite = pygame.image.load('Assets/health.png')
        width, height = sprite.get_width(), sprite.get_height()
        self.sprite = pygame.transform.scale(sprite, (width * self.scale, height * self.scale))
        self.health = random.randrange(25, 50)
    
        
    def draw(self, offset):
        float_position = self.position - offset
        float_position.y += self.float_offset
        self.display.blit(self.sprite, float_position)