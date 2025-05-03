import pygame
import UserInterface
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



class MenuScene(Scene):
    def __init__(self, SceneManager):
        super().__init__(SceneManager)
        self.background = pygame.image.load('Assets/Title.png')
        self.play_button = UserInterface.TextureButton((340, 340), 'Assets/UI/Start Button.png', self.start_game, 3)
        self.quit_button = UserInterface.TextureButton((340, 440), 'Assets/UI/Quit Button.png', self.quit_game, 3)
    
    
    def update(self):
        self.play_button.update()
        self.quit_button.update()
    
    
    def start_game(self):
        self.SceneManager.switch_scene('GameScene')
    
    
    def quit_game(self):
        print(self.SceneManager.running)
        self.SceneManager.running = False
    
    
    def draw(self):
        display = pygame.display.get_surface()
        display.blit(self.background, (0, 0))
        self.play_button.draw()
        self.quit_button.draw()


class GameScene(Scene):
    def __init__(self, sceneManager):
        super().__init__(sceneManager)
        self.CameraGroup = CameraGroup()
        self.world = World()
        self.player = Player(None, self.CameraGroup)
        self.player.position = pygame.math.Vector2(550, 600)
        
        self.world.initialize_shop(self.player)
        
        icon = pygame.image.load('Assets/UI/Souls.png')
        w, h = icon.get_width(), icon.get_height()
        self.souls_ui = {
            'Icon' : pygame.transform.scale(icon, (w*3, h*3)),
            'Text' : font.render('x 0', False, 'White')
        }

        self.player.world = self.world
        self.world.player = self.player
        
    
    def update(self, dt):
        if self.world.shop.closed:
            self.world.shop_open = False
            self.world.shop.closed = False
        
        if not self.world.shop_open:
            self.CameraGroup.update(dt)
            self.world.update(dt)
        else:
            self.world.shop.update()
        
        self.souls_ui['Text'] = font.render(f'x {self.player.souls}', False, 'White')
    
    
    def draw(self):
        surface = pygame.display.get_surface()
        self.world.draw(self.CameraGroup.offset)
        self.CameraGroup.draw(self.player)
        
        if self.world.shop_open:
            self.world.shop.draw()    
        
        surface.blit(self.souls_ui['Icon'], (60, 20))
        surface.blit(self.souls_ui['Text'], (90, 20))
        