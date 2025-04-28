import pygame
from player import Player
from world import World
from CameraGroup import CameraGroup

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

        self.player.world = self.world
        self.world.player = self.player
        
    
    def update(self, dt):
        self.CameraGroup.update(dt)
        self.world.update(dt)
    
    
    def draw(self):
        surface = pygame.display.get_surface()
        self.world.draw(self.CameraGroup.offset)
        self.CameraGroup.draw(self.player)