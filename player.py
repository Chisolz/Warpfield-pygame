import pygame
import gun
import math
from spritesheet import Spritesheet
from UserInterface import HealthBar

class Player(pygame.sprite.Sprite):
    
    def __init__(self, world, group):
        super().__init__(group)
        self.health = 200
        self.maxHealth = 200
        self.playerHP = HealthBar(0, 0, 60, 15, self.maxHealth)
        self.world = world
        self.flipped = False
        self.scale = 3
        self.position = pygame.math.Vector2(0, 0)
        self.old_pos = pygame.math.Vector2(0, 0)
        self.speed = 300
        self.moving = False
        self.rect = pygame.Rect(0, 0, 35, 40)
        self.rect.topleft = (self.position.x, self.position.y)
        self.spritesheet = Spritesheet("Assets/Player/Player.png")
        self.gun = gun.Gun()
        self.gun.select_gun('pistol')
        self.sway_amplitude = 10
        self.sway_speed = 10
        self.sway_time = 0
        self.offset_x = None
        self.canShoot = True
        self.lastShot = 0
        self.animationTime = 0.04
        self.frameIdx = 1
        self.frameTime = 0
        self.sprites = [
            self.spritesheet.parseSprite('Idle-0'),
            self.spritesheet.parseSprite('Idle-1')
        ]
        self.spritesFlipped = [
            pygame.transform.flip(self.sprites[0], True, False),
            pygame.transform.flip(self.sprites[1], True, False)
        ]
        self.selectedSprite = pygame.transform.scale(self.sprites[0], (12 * 3, 12 * 3))
        
        self.souls = 0 # Currency in-game
        
        self.stats = {
            'Trigger Happy': 0, # Fire rate modifier
            'Pocket Bullets': 0, # Bps modifier
            'Accurate': 0, # Bullet spread modifier
            'Juice Up': 0, # Health modifier
            'Hard Noggin': 0 # Defense modifier
        }
        
        # I-Frames setup
        self.invincible = False
        self.i_frame_duration = 1000
        self.last_hit_time = 0
    
    
    def update(self, dt, offset):
        self.moving = False
        keys = pygame.key.get_pressed()
        gun_data = self.gun.gunData[self.gun.gunName]
        mousePos = pygame.mouse.get_pos()
        adjusted_mouse_position = (
            mousePos[0] + offset.x,
            mousePos[1] + offset.y
        )
        current_time = pygame.time.get_ticks()
        # Loop through Idle animation
        self.frameTime += self.animationTime
        if self.frameTime >= 1:
            self.frameIdx = (self.frameIdx + 1) % len(self.sprites)
            self.frameTime = 0
        
        # Shot cooldown
        if current_time - self.lastShot >= max(100, gun_data['fire rate'] - self.stats['Trigger Happy']):
            self.canShoot = True
            
        # Check if health is greater than max
        if self.health > self.maxHealth:
            self.health = self.maxHealth
        
        # Check if health is below or equal to 0
        if self.health <= 0:
            pass
            
        # Check if I-Frames expired
        if self.invincible and current_time - self.last_hit_time >= self.i_frame_duration:
            self.invincible = False 
        
        # Check if hit by bullet
        for bullet in self.world.bullets:
            if self.rect.colliderect(bullet.rect) and bullet.shotBy == 'Enemy' and not self.invincible:
                bullet.dead = True
                self.health -= max(5, bullet.damage - self.stats['Hard Noggin'])
                self.invincible = True
                self.last_hit_time = current_time
        
        for item in self.world.items:
            if self.rect.colliderect(item.rect):
                item.in_contact = True
                if item.type == 'health':
                    item.equipped = True
                    self.health += item.health
                if item.type == 'gun':
                    if keys[pygame.K_e]:
                        item.equipped = True
                        self.gun.select_gun(item.name)
            
            else:
                item.in_contact = False
        
        # Get mouse input 
        if pygame.mouse.get_pressed()[0] and self.canShoot:
            self.canShoot = False
            self.lastShot = current_time
            x = adjusted_mouse_position[0] - self.position.x
            y = adjusted_mouse_position[1] - self.position.y
            vector = pygame.math.Vector2(x, y)
            vectorNormal = vector.normalize()
            spawnPos = (self.gun.offset_position[0], self.gun.offset_position[1])
            
            data = gun_data
            data['spread'] = max(0, data['spread'] - self.stats['Accurate'])
            
            for _ in range(gun_data['bps'] + self.stats['Pocket Bullets']):
                self.world.bullets.append(gun.Bullet(spawnPos, 'Player', vectorNormal, self.world, data))
        
        new_pos = self.position.copy()
        
        # Get Vertical Direction
        if keys[pygame.K_w]:
            new_pos.y -= self.speed * dt 
            self.moving = True
        elif keys[pygame.K_s]:
            new_pos.y += self.speed * dt
            self.moving = True
            
        
        for tile in self.world.world_group:
            if tile.collision:
                new_pos = self.handle_tile_collision(new_pos, tile, 'vertical')
        

        # Get Horizontal Direction
        if keys[pygame.K_a]:
            new_pos.x -= self.speed * dt
            self.moving = True
        elif keys[pygame.K_d]:
            new_pos.x += self.speed * dt
            self.moving = True
        
        # Flip player sprite based on the mouse's X position
        if adjusted_mouse_position[0] < self.position.x:
            self.selectedSprite = pygame.transform.scale(self.spritesFlipped[self.frameIdx], (12 * self.scale, 12 * self.scale))
        else:
            self.selectedSprite = pygame.transform.scale(self.sprites[self.frameIdx], (12 * self.scale, 12 * self.scale))
        
        # Sway the character sprite if moving
        if self.moving:
            self.sway_time += dt * self.sway_speed
        else:
            self.sway_time = 0
        
        self.offset_x = math.sin(self.sway_time) * self.sway_amplitude
        
        # Update gun and player rectangle
        self.rect.topleft = [self.position.x, self.position.y]
        self.gun.update(self.rect.center, mousePos, offset)
        
        
        for tile in self.world.world_group:
            if tile.collision:
                new_pos = self.handle_tile_collision(new_pos, tile, 'horizontal')
                
        self.position = new_pos
        
        # Change health bar value
        self.playerHP.value = self.health
        self.playerHP.maxValue = self.maxHealth
        self.playerHP.update()
        
        # Store health bar position in local variable
        health_bar_position = pygame.math.Vector2(self.rect.bottomleft[0] - 35, self.rect.bottomleft[1] + 10)
        
        self.playerHP.x = health_bar_position.x
        self.playerHP.y = health_bar_position.y
    
    
    def handle_tile_collision(self, new_position, tile, axis):
        temp_rect = pygame.Rect(new_position.x, new_position.y, self.rect.width, self.rect.height)
    
        # If checking for horizontal movement
        if axis == 'horizontal':
            if temp_rect.colliderect(tile.rect):
                if temp_rect.right > tile.rect.left and temp_rect.left < tile.rect.right:
                    # Collided from the right, stop the rightward movement
                    if self.position.x < new_position.x:
                        new_position.x = tile.rect.left - self.rect.width  # Prevent moving through the tile
                    elif self.position.x > new_position.x:
                        new_position.x = tile.rect.right  # Prevent moving through the tile
    
        # If checking for vertical movement
        if axis == 'vertical':
            if temp_rect.colliderect(tile.rect):
                if temp_rect.bottom > tile.rect.top and temp_rect.top < tile.rect.bottom:
                    # Collided from below, stop the downward movement
                    if self.position.y < new_position.y:
                        new_position.y = tile.rect.top - self.rect.height  # Prevent moving through the tile
                    elif self.position.y > new_position.y:
                        new_position.y = tile.rect.bottom  # Prevent moving through the tile
    
        return new_position
    
    
    def draw(self, window, offset):
        if self.invincible: # Flash player sprite if invincible
            current_time = pygame.time.get_ticks()
            if (current_time // 100) % 2 == 0:
                return
        
        rotation_angle = math.sin(self.sway_time) * self.sway_amplitude
        rotated_sprite = pygame.transform.rotate(self.selectedSprite, rotation_angle)
        rotated_rect = rotated_sprite.get_rect(center=(self.position.x, self.position.y))

        window.blit(rotated_sprite, rotated_rect.topleft - offset)
        self.gun.draw(window, offset)
        
        self.playerHP.draw(window, offset)
        
