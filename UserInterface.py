import pygame
from spritesheet import Spritesheet

class HealthBar():
    def __init__(self, x, y, width, height, maxValue):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = maxValue
        self.maxValue = maxValue
        self.outerRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.innerRect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    
    def update(self):
        ratio = self.value / self.maxValue
        self.innerRect.width = self.width * ratio
        
        self.innerRect.topleft = (self.x, self.y)
        self.outerRect.topleft = (self.x, self.y)
    
    
    def draw(self, surface, offset):
        if self.value < self.maxValue:
            pygame.draw.rect(surface, 'red', self.outerRect.move(-offset))
            pygame.draw.rect(surface, 'green', self.innerRect.move(-offset))



class PickupUI():
    def __init__(self, position):
        spritesheet = Spritesheet('Assets/pickup ui.png')
        self.surface = pygame.display.get_surface()
        self.frameIdx = 0
        self.frameTime = 0
        self.animationTime = 0.50
        self.frames = []
        self.position = position #+ pygame.math.Vector2(10, 30)

        for i in range(9):
            frame = spritesheet.parseSprite(str(i))
            width, height = frame.get_width(), frame.get_height()
            frameScaled = pygame.transform.scale(frame, (width * 3, height*3))
            self.frames.append(frameScaled)

    
    def play_anim(self):
        self.frameTime += self.animationTime
        if self.frameTime >= 1:
            if self.frameIdx < len(self.frames) - 1:  # Stop at the last frame
                self.frameIdx += 1
            self.frameTime = 0
    
    
    def reset_anim(self):
        self.frameIdx = 0
        self.frameTime = 0
    
    
    def draw(self, position):
        frame = self.frames[self.frameIdx]
        self.surface.blit(frame, position)