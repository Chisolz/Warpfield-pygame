import pygame
import Scenes


class SceneManager:
    def __init__(self):
        self.selected_scene = None
        self.running = False
        self.scenes = {}

    def add_scene(self, name, scene):
        self.scenes[name] = lambda: scene

    def switch_scene(self, name):
        if name in self.scenes:
            self.selected_scene = self.scenes[name]()
        else:
            print(f"Scene {name} not found!")

    def restart_scene(self):
        if self.selected_scene:
            scene_name = type(self.selected_scene).__name__
            if scene_name in self.scenes:
                self.selected_scene = self.scenes[scene_name]()

    def get_scene(self, name):
        if name in self.scenes:
            return self.scenes[name]()
        else:
            print(f"Scene {name} not found!")
            return None

    def get_current_scene(self):
        return self.selected_scene
    