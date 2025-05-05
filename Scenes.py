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
        pygame.mixer.music.unload()
        
    
    def cleanup(self):
        pass
    
    
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
    
    
    def cleanup(self):
        self.background = None
        self.play_button = None
        self.quit_button = None
    
    
    def update(self, dt):
        if pygame.mixer.music.get_busy() == False:
            pygame.mixer.music.load('Music/Menu Theme.ogg')
            pygame.mixer.music.play(-1)
        
        self.play_button.update()
        self.quit_button.update()
    
    
    def start_game(self):
        self.SceneManager.switch_scene('GameScene')
    
    
    def quit_game(self):
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
    
    
    def cleanup(self):
        # Clean up world first
        if self.world:
            self.world.cleanup()
            self.world = None
        
        # Clean up player and camera group
        if self.player:
            self.player.kill()
            self.player = None
        
        if self.CameraGroup:
            self.CameraGroup.empty()
            self.CameraGroup = None
        
        # Clean up UI elements
        self.souls_ui = None
        
        # Force garbage collection
        import gc
        gc.collect()
    
    
    def update(self, dt):
        if pygame.mixer.music.get_busy() == False:
            pygame.mixer.music.load('Music/Main Theme.ogg')
            pygame.mixer.music.play(-1)
        
        if self.world.shop.closed:
            self.world.shop_open = False
            self.world.shop.closed = False
        
        if not self.world.shop_open:
            self.CameraGroup.update(dt)
            self.world.update(dt)
        else:
            self.world.shop.update()
            
        if self.player.health <= 0:
            self.SceneManager.switch_scene('Game Over')
        
        self.souls_ui['Text'] = font.render(f'x {self.player.souls}', False, 'White')
    
    
    def draw(self):
        surface = pygame.display.get_surface()
        self.world.draw(self.CameraGroup.offset)
        self.CameraGroup.draw(self.player)
        
        if self.world.shop_open:
            self.world.shop.draw()    
        
        surface.blit(self.souls_ui['Icon'], (60, 20))
        surface.blit(self.souls_ui['Text'], (90, 20))



class GameOver(Scene):
    def __init__(self, SceneManager, world):
        super().__init__(SceneManager)
        self.world = world
        self.text = font.render('Game Over!', False, 'White')
        self.waves_survived = font.render(f'You survived {self.world.current_wave} waves.', False, 'White')
        self.retry_button = UserInterface.Button(375, 200, 100, 50, self.retry_game, 'grey', 'Retry?')
        self.quit_button = UserInterface.Button(375, 300, 100, 50, self.SceneManager.quit_game, 'grey', 'Quit')
    
    
    def cleanup(self):
        # Clean up world
        if self.world:
            self.world.cleanup()
            self.world = None
        
        # Clean up UI elements
        self.text = None
        self.waves_survived = None
        self.retry_button = None
        self.quit_button = None
        
        # Force garbage collection
        import gc
        gc.collect()
    
    
    def retry_game(self):
        self.SceneManager.switch_scene('GameScene')
        self.SceneManager.restart_scene()
    
    
    def update(self, dt):
        if pygame.mixer.music.get_busy() == False:
            pygame.mixer.music.load('Music/Game Over Theme.ogg')
            pygame.mixer.music.play(-1)
        
        self.retry_button.update()
        self.quit_button.update()
    
    
    def draw(self):
        surface = pygame.display.get_surface()
        surface.blit(self.text, (375, 50))
        self.retry_button.draw()
        self.quit_button.draw()
        
        