import pygame
import Scenes
from SceneManager import SceneManager

pygame.init()
pygame.font.init()

Window = pygame.display.set_mode((850, 600))
Clock = pygame.time.Clock()
running = True
DeltaTime = 0
pygame.display.set_caption('Warpfield')

scene_manager = SceneManager()
scene_manager.add_scene('GameScene', Scenes.GameScene(scene_manager))
scene_manager.switch_scene('GameScene')
GameScene = scene_manager.get_current_scene()
while running:
    DeltaTime = Clock.tick(60) / 1000
    DeltaTime = max(0.001, min(DeltaTime, 0.1))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                if scene_manager.selected_scene.world.debug:
                    GameScene.world.debug = False
                else:
                    GameScene.world.debug = True

    scene_manager.selected_scene.update(DeltaTime)
    
    Window.fill('#141A36')
    
    scene_manager.selected_scene.draw()
    
    pygame.display.flip()
pygame.quit()