import pygame
from tile import Tile
from player import Player

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        
        self.offset = pygame.math.Vector2()
        
        # Camera Lock Setup
        self.camLockRect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        
        # Camera Rect Setup
        self.cameraBorders = {'left': 75, 'right': 75, 'top': 75, 'bottom': 75}
        l = self.cameraBorders['left']
        t = self.cameraBorders['top']
        w = self.screen.get_width() - (self.cameraBorders['left'] + self.cameraBorders['right'])
        h = self.screen.get_height() - (self.cameraBorders['top'] + self.cameraBorders['bottom'])
        self.cameraRect = pygame.Rect(l, t, w, h)
    
    
    def box_target(self, target):
        if target.rect.left < self.cameraRect.left:
            self.cameraRect.left = target.rect.left
        if target.rect.right > self.cameraRect.right:
            self.cameraRect.right = target.rect.right
        if target.rect.top < self.cameraRect.top:
            self.cameraRect.top = target.rect.top
        if target.rect.bottom > self.cameraRect.bottom:
            self.cameraRect.bottom = target.rect.bottom 
        
        self.offset.x = self.cameraRect.left - self.cameraBorders['left']
        self.offset.y = self.cameraRect.top - self.cameraBorders['top']
    

    def update(self, dt):
        for sprite in self.sprites():
            if isinstance(sprite, Player):
                sprite.update(dt, self.offset)
    
    
    def draw(self, player):
        self.box_target(player)
        drawable_sprites = sorted(
            (sprite for sprite in self.sprites() if not isinstance(sprite, Tile)),
            key=lambda sprite: sprite.position.y
        )

        
        for sprite in drawable_sprites:
            sprite.draw(self.screen, self.offset)