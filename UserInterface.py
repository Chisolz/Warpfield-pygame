import pygame

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
        