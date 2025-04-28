import pygame
import random
from spritesheet import Spritesheet, Tilemap

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.tilemap = Tilemap('Assets/Map/Map.png')
        self.sprites = []
        self.scale = 3
        self.position = pos
        self.id = 0
        self.selectedTile = None
        self.tile = None
        self.collision = False
        
        for i in range(len(self.tilemap.images)-1):
            image = self.tilemap.images[i]
            width, height = image.get_width(), image.get_height()
            imageScaled = pygame.transform.scale(image, (width * self.scale, height * self.scale))
            self.sprites.append(imageScaled)
            
        self.rect = self.sprites[0].get_rect()
        self.rect.x = int(pos.x)
        self.rect.y = int(pos.y)
        self.rgb = random.randint(1, 3)
        
    
    def set_current(self, id):
        image = self.sprites[id]
        props = self.tilemap.tileProperties.get(id)
        self.collision = False
        
        if props:
            for prop in props:
                if prop['name'] == 'hasCollision':
                    self.collision = prop['value']
                    
        self.selectedTile = image
        
    
    def draw(self, window, offset):
        if self.selectedTile:
            window.blit(self.selectedTile, self.position - offset)
