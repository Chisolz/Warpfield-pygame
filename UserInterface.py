import pygame
from spritesheet import Spritesheet

pygame.font.init()
font = pygame.font.Font('Assets/Font/VT323-Regular.ttf', size=30)

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
        spritesheet = Spritesheet('Assets/UI/pickup ui.png')
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



class Button():
    def __init__(self, x, y, w, h, callback, color='grey', text=None, textColor='White'):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.callback = callback
        self.hovering = False
        self.text = None
        
        if text != None:
            self.text = font.render(text, False, textColor)
    
    
    def update(self):
        self.hovering = False
        mouseButtons = pygame.mouse.get_just_pressed()
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovering = True
            if mouseButtons[0]:
                self.callback()
    
    
    def draw(self):
        display = pygame.display.get_surface()
        pygame.draw.rect(display, self.color, self.rect)
        
        if self.text == None:
            return
        
        display.blit(self.text, self.text.get_rect(center=self.rect.center))



class TextureButton(Button):
    def __init__(self, position, image, callback, scale=1):
        self.scale = scale
        self.position = position
        
        img = pygame.image.load(image)
        w, h = img.get_width(), img.get_height()
        scaled = pygame.transform.scale(img, (w*scale, h*scale))
        
        self.image = scaled
        size = self.image.get_size()
        super().__init__(position[0], position[1], size[0], size[1], callback)
        
        
    def draw(self):
        display = pygame.display.get_surface()
        display.blit(self.image, (self.position))