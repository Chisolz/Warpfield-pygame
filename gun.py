import pygame
import math
import json
import random
from pathlib import Path


class Gun:
    def __init__(self):
        self.guns = {}
        self.gunsFlipped = {}
        assets = Path('Assets/Guns')
        for file in assets.iterdir():
            if file.is_file():
                if file.name.endswith('.png'):
                    name = file.name.removesuffix('.png')
                    gun = pygame.image.load(file).convert_alpha()
                    gunScaled = pygame.transform.scale(gun, (gun.get_width()*3, gun.get_height()*3))
                    flipped = pygame.transform.flip(gunScaled, False, True)
                    self.guns[name] = gunScaled
                    self.gunsFlipped[name] = flipped
                elif file.name.endswith('.json'):
                    with open(file) as f:
                        self.gunData = json.load(f)
                        f.close()
                    
        self.selectedGun = None
        self.rotated_gun = None
        self.offset_position = (0, 0)
        self.gunName = None
    
    
    def select_gun(self, gunName):
        if gunName in self.guns:
            self.gunName = gunName
            self.selectedGun = self.guns[gunName]
    
    
    def update(self, player_position, mouse_position, camera_offset):
        # Only update if selected gun is not None
        if self.selectedGun:
            
            adjusted_mouse_position = (
                mouse_position[0] + camera_offset.x,
                mouse_position[1] + camera_offset.y
            )

            
            # Make gun follow the mouse
            dx = adjusted_mouse_position[0] - player_position[0]
            dy = adjusted_mouse_position[1] - player_position[1]
            angle = math.degrees(math.atan2(dy, dx))

            # Flip gun if mouse position is greater than the player
            if adjusted_mouse_position[0] > player_position[0]:
                self.selectedGun = self.guns[self.gunName]
            else:
                self.selectedGun = self.gunsFlipped[self.gunName]

            # Rotate gun
            self.rotated_gun = pygame.transform.rotate(self.selectedGun, -angle)

            offset_x, offset_y = self.gunData[self.gunName]['offsetX'], self.gunData[self.gunName]['offsetY']
            self.offset_position = (player_position[0] + offset_x, player_position[1] + offset_y)

    def Eupdate(self, enemy_position, aim_direction):
        # Only update if selected gun is not None
        if self.selectedGun:

            angle = math.degrees(math.atan2(-aim_direction.y, aim_direction.x))

            self.rotated_gun = pygame.transform.rotate(self.selectedGun, -angle)

            offset_x = self.gunData[self.gunName]['offsetX']
            offset_y = self.gunData[self.gunName]['offsetY']
            self.offset_position = (enemy_position.x, enemy_position.y)
    
    def draw(self, window, offset):
        x = self.offset_position[0]
        y = self.offset_position[1]
        window.blit(self.rotated_gun, (x - offset.x, y - offset.y))


class Bullet:
    def __init__(self, spawnPos, shotBy, direction, world, gunData):
        # Load bullet sprite
        image = pygame.image.load('Assets/bullet.png').convert()
        w, h = image.get_width(), image.get_height()
        scale = 2

        # Spread angle in degrees
        spread_degrees = gunData.get('spread', 0)  # Default 0 if not defined

        # Apply random spread to the direction vector
        base_angle = math.atan2(direction.y, direction.x)
        spread_radians = math.radians(random.uniform(-spread_degrees / 2, spread_degrees / 2))
        new_angle = base_angle + spread_radians

        # Create new direction vector from the spread angle
        self.direction = pygame.math.Vector2(math.cos(new_angle), math.sin(new_angle))

        # Rotate sprite accordingly
        sprite = pygame.transform.scale(image, (w * scale, h * scale))
        angle_degrees = math.degrees(-new_angle)
        self.sprite = pygame.transform.rotate(sprite, angle_degrees - 90)
        self.sprite.set_colorkey((0, 0, 0))

        self.speed = gunData['speed']
        self.damage = gunData['damage']
        self.world = world
        self.dead = False
        self.position = pygame.math.Vector2(spawnPos[0], spawnPos[1])
        self.rect = self.sprite.get_rect()
        self.shotBy = shotBy
        

    def update(self, dt):
        self.position += self.direction * self.speed * dt
        self.rect.center = (self.position.x + 5, self.position.y + 5)

        for tile in self.world.world_group:
            if tile.collision and self.rect.colliderect(tile.rect):
                self.dead = True

    def draw(self, screen, offset):
        screen.blit(self.sprite, (self.position.x - offset.x, self.position.y - offset.y))