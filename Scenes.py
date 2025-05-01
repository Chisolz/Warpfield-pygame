import pygame
from player import Player
from world import World
from CameraGroup import CameraGroup

pygame.font.init()
font = pygame.font.Font('Assets/Font/VT323-Regular.ttf', size=30)

class Scene:
    def __init__(self, SceneManager=None):
        self.SceneManager = SceneManager
        
    
    def update(dt):
        pass
    
    
    def draw():
        pass


class GameScene(Scene):
    def __init__(self, sceneManager):
        super().__init__(sceneManager)
        self.CameraGroup = CameraGroup()
        self.world = World()
        self.player = Player(None, self.CameraGroup)
        self.player.position = pygame.math.Vector2(550, 600)
        self.waves_text = font.render('Wave 1', False, 'White')

        self.player.world = self.world
        self.world.player = self.player
        
    
    def update(self, dt):
        self.CameraGroup.update(dt)
        self.world.update(dt)
    
    
    def draw(self):
        surface = pygame.display.get_surface()
        self.world.draw(self.CameraGroup.offset)
        self.CameraGroup.draw(self.player)
        surface.blit(self.waves_text, (90, 20))