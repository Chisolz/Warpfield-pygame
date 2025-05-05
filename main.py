import pygame
import Scenes
from SceneManager import SceneManager
from UserInterface import TextureButton

from StatStore import StatShop

pygame.init()

Window = pygame.display.set_mode((850, 600))
Clock = pygame.time.Clock()
DeltaTime = 0
pygame.display.set_caption('Warpfield')

scene_manager = SceneManager()
scene_manager.add_scene('Main Menu', Scenes.MenuScene(scene_manager))
scene_manager.add_scene('GameScene', Scenes.GameScene(scene_manager))
scene_manager.add_scene('Game Over', Scenes.GameOver(scene_manager, scene_manager.get_scene('GameScene').world))
scene_manager.switch_scene('Main Menu')
scene_manager.running = True

while scene_manager.running:
    DeltaTime = Clock.tick(60) / 1000
    DeltaTime = max(0.001, min(DeltaTime, 0.1))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            scene_manager.quit_game()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                game_scene = scene_manager.get_scene('GameScene')
                if game_scene.world.debug:
                    game_scene.world.debug = False
                else:
                    game_scene.world.debug = True

    scene_manager.selected_scene.update(DeltaTime)
    
    Window.fill('#141A36')
    scene_manager.selected_scene.draw()
    pygame.display.flip()

pygame.quit()