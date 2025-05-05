import pygame
import Scenes


class SceneManager:
    def __init__(self):
        self.selected_scene = None
        self.running = False
        self.scenes = {}

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def switch_scene(self, name):
        pygame.mixer.music.unload()
        if name in self.scenes:
            self.selected_scene = self.scenes[name]
        else:
            print(f"Scene {name} not found!")

    def restart_scene(self):
        if self.selected_scene:
            # Call the cleanup method for the current scene
            self.selected_scene.cleanup()

            # Find the name of the current scene
            scene_name = None
            for key, value in self.scenes.items():
                if value == self.selected_scene:
                    scene_name = key
                    break

            if scene_name:
                # Recreate the scene
                scene_class = type(self.scenes[scene_name])
                self.scenes[scene_name] = scene_class(self)
                self.selected_scene = self.scenes[scene_name]
            else:
                print("Current scene not found in scenes dictionary!")

    def get_scene(self, name):
        if name in self.scenes:
            return self.scenes[name]
        else:
            print(f"Scene {name} not found!")
            return None

    def get_current_scene(self):
        return self.selected_scene

    def quit_game(self):
        self.running = False
    