import pygame
import random
import math
import gun
import ItemDrops
from UserInterface import HealthBar

bulletSounds = [
    pygame.mixer.Sound('Sounds/explosion (1).wav'), # Shotgun sound 1 
    pygame.mixer.Sound('Sounds/explosion.wav'), # Shotgun sound 2
    pygame.mixer.Sound('Sounds/laserShoot (1).wav'), # Generic Shot Sound 1
    pygame.mixer.Sound('Sounds/laserShoot (2).wav'), # Generic Shot Sound 2
    pygame.mixer.Sound('Sounds/laserShoot.wav') # Generic Shot Sound 3
]

for sound in bulletSounds:
    sound.set_volume(0.2)


class Enemy:
    def __init__(self, world, hp, scale, sightRadius):
        self.world = world
        self.in_world = True
        self.flipped = False
        self.position = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(0, 0)
        self.state = None
        self.sprite = None
        self.original_sprite = None
        self.flash_timer = 0
        self.sightRadius = sightRadius
        self.innerRadius = sightRadius - 50
        self.moving = False
        self.scale = scale
        self.dead = False
        self.speed = 100
        self.new_pos = self.position.copy()
        self.health = hp
        self.healthbar = HealthBar(0, 0, 60, 15, hp)
        self.picking_time = 5000
        self.strafe_timer = 0
        self.strafe_dir = 1
        self.sway_amplitude = 10
        self.sway_speed = 10
        self.sway_time = 0
        self.offset_x = None
        self.canShoot = True
        self.killed = False
        self.lastShot = 0
        self.gun = gun.Gun()
        self.gun.select_gun('pistol')
        self.rect = pygame.Rect(self.position.x, self.position.y, 50, 50)


    def update(self, dt):
        
        inMap = False
        
        for bullet in self.world.bullets: # Check if hit by bullet
            if self.rect.colliderect(bullet.rect) and bullet.shotBy == 'Player': # Check if bullet was shot by player
                bullet.dead = True
                self.flash_red()
                self.health -= bullet.damage
        
        for tile in self.world.world_group: # Check if enemy is inside the map
            if self.rect.colliderect(tile.rect):
                inMap = True
                break

        if self.health <= 0: # Confirms if enemy is dead
            self.world.items.append(self.drop_item())
            self.killed = True
            self.dead = True
        
        if inMap == False:
            self.dead = True

        if self.direction.length_squared() != 0: # Normalize direction
            self.direction = self.direction.normalize()

        if self.direction.x < 0: # Flip gun based on direction
            self.flipped = True
        else:
            self.flipped = False
            
        if self.flash_timer > 0: # Reset enemy sprite after flash effect
            self.flash_timer -= dt * 1000
            if self.flash_timer <= 0:
                self.sprite = self.original_sprite.copy()

        move = self.direction * self.speed * dt
        new_position = self.position + move
        new_position = self.resolve_collisions(new_position)

        self.sway_time += dt * self.sway_speed
        self.offset_x = math.sin(self.sway_time) * self.sway_amplitude

        self.gun.Eupdate(self.position, -self.direction)

        self.position = new_position
        self.rect.topleft = (self.position.x, self.position.y)
        
        # Change health bar value
        self.healthbar.value = self.health
        self.healthbar.update()
        
        # Store health bar position in local variable
        health_bar_position = pygame.math.Vector2(self.rect.bottomleft[0] - 35, self.rect.bottomleft[1] + 10)
        
        self.healthbar.x = health_bar_position.x
        self.healthbar.y = health_bar_position.y

    def resolve_collisions(self, new_position):
        # Move horizontally
        temp_rect = pygame.Rect(new_position.x, self.position.y, self.rect.width, self.rect.height)

        for tile in self.world.world_group:
            if tile.collision:
                if temp_rect.colliderect(tile.rect):
                    if new_position.x > self.position.x:  # Moving right
                        new_position.x = tile.rect.left - self.rect.width
                        break
                    elif new_position.x < self.position.x:  # Moving left
                        new_position.x = tile.rect.right
                        break

        # Move vertically
        temp_rect = pygame.Rect(new_position.x, new_position.y, self.rect.width, self.rect.height)

        for tile in self.world.world_group:
            if tile.collision:
                if temp_rect.colliderect(tile.rect):
                    if new_position.y > self.position.y:  # Moving down
                        new_position.y = tile.rect.top - self.rect.height
                        break
                    elif new_position.y < self.position.y:  # Moving up
                        new_position.y = tile.rect.bottom
                        break

        return new_position


    def circle_rect_collision(self, circle_radius, rect):
        closest_x = max(rect.left, min(self.position.x, rect.right))
        closest_y = max(rect.top, min(self.position.y, rect.bottom))
        distance_x = self.position.x - closest_x
        distance_y = self.position.y - closest_y
        return (distance_x ** 2 + distance_y ** 2) < (circle_radius ** 2)
    
    
    def flash_red(self):
        if self.original_sprite:
            self.sprite = self.original_sprite.copy()
            red_overlay = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 100))
            self.sprite.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.flash_timer = 100
    
    
    def drop_item(self):
        index = random.randrange(1, 3)
        if index == 1 or index == 3:
            return ItemDrops.Gun(self.position, self.gun.gunName)
        elif index == 2:
            return ItemDrops.HealthDrop(self.position)
    

    def draw(self, window, offset):
        self.healthbar.draw(window, offset)


class Skeleboi(Enemy):
    def __init__(self, world, position):
        super().__init__(world, 75, 3, 250)
        sprite = pygame.image.load('Assets/Enemies/SkeleBoy.png').convert()
        w, h = sprite.get_width(), sprite.get_height()
        sprite.set_colorkey((0, 0, 0))
        self.sprite = pygame.transform.scale(sprite, (w * self.scale, h * self.scale))
        self.original_sprite = self.sprite.copy()
        self.rect = pygame.Rect(position.x, position.y, self.sprite.get_width(), self.sprite.get_height())
        self.position = position.copy()
        self.rect.topleft = position
        self.last_pick = 0
        self.can_pick = True
        self.new_pos = self.position.copy()
        self.speed = 150
        
        index = random.randint(1, 3)
        if index == 1:
            self.gun.select_gun('pistol')
        elif index == 2:
            self.gun.select_gun('smg')
        else: 
            self.gun.select_gun('sniper')


    def update(self, dt):
        current_time = pygame.time.get_ticks()
        gunData = self.gun.gunData[self.gun.gunName]
        desired_distance = 150
        to_player = self.world.player.position - self.position
        distance = to_player.length()
        direction = to_player.normalize() if distance != 0 else pygame.Vector2(0, 0)

        if current_time - self.last_pick >= self.picking_time:
            self.can_pick = True
        if current_time - self.lastShot >= gunData['fire rate']:
            self.canShoot = True
        
        inSight = self.circle_rect_collision(self.sightRadius, self.world.player.rect)
        inRange = self.circle_rect_collision(self.innerRadius, self.world.player.rect)
        if inRange and self.canShoot:
            self.state = 'Shooting'
        elif inSight:
            self.state = 'Follow'
        else:
            self.state = 'Roam'

        if self.state == 'Follow':
            self.direction = direction
            self.strafe_timer += dt
            if self.strafe_timer >= 1.0:
                self.strafe_timer = 0
                self.strafe_dir *= -1

            strafe = pygame.math.Vector2(-direction.y, direction.x) * self.strafe_dir * 0.5

            if distance > desired_distance + 10:
                self.direction = (direction + strafe).normalize()
            elif distance < desired_distance - 10:
                self.direction = (-direction + strafe).normalize()
            else:
                self.direction = strafe.normalize() if strafe.length_squared() != 0 else pygame.math.Vector2(0, 0)

        elif self.state == 'Shooting':
            if self.canShoot:
                self.canShoot = False
                self.lastShot = current_time
                if self.gun.gunName == 'shotgun' or self.gun.gunName == 'sniper':
                    bulletSounds[random.randrange(0, 1)].play()
                else:
                    bulletSounds[random.randrange(2, 4)].play()
                for _ in range(gunData['bps']):
                    bullet = gun.Bullet(self.position, 'Enemy', to_player, self.world, gunData)
                    self.world.bullets.append(bullet)

        elif self.state == 'Roam':
            if self.can_pick:
                self.can_pick = False
                self.last_pick = current_time
                choice = random.randrange(1, 5)
                if choice in [1, 2]:
                    self.direction = direction
                else:
                    dir = pygame.math.Vector2(random.randrange(-10, 10), random.randrange(-10, 10))
                    if dir.length_squared() != 0:
                        self.direction = dir.normalize()
                    else:
                        self.direction = pygame.math.Vector2(1, 0)
        
        super().update(dt)

    def draw(self, window, offset):
        rotation_angle = math.sin(self.sway_time) * self.sway_amplitude
        rotated_sprite = pygame.transform.rotate(self.sprite, rotation_angle)
        window.blit(rotated_sprite, self.position - offset)
        self.gun.draw(window, offset)
        super().draw(window, offset)



class DevilDare(Enemy):
    def __init__(self, world, position):
        super().__init__(world, 150, 3, 200)
        sprite = pygame.image.load('Assets/Enemies/DevilDare.png').convert()
        w, h = sprite.get_width(), sprite.get_height()
        sprite.set_colorkey((0, 0, 0))
        self.sprite = pygame.transform.scale(sprite, (w * self.scale, h * self.scale))
        self.original_sprite = self.sprite.copy()
        self.rect = pygame.Rect(position.x, position.y, self.sprite.get_width(), self.sprite.get_height())
        self.position = position.copy()
        self.rect.topleft = position
        self.last_pick = 0
        self.can_pick = True
        self.new_pos = self.position.copy()
        
        index = random.randint(1, 3)
        if index == 1:
            self.gun.select_gun('shotgun')
        elif index == 2:
            self.gun.select_gun('smg')
        else: 
            self.gun.select_gun('sniper')
    
    
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        gunData = self.gun.gunData[self.gun.gunName]
        desired_distance = 125
        to_player = self.world.player.position - self.position
        distance = to_player.length()
        direction = to_player.normalize() if distance != 0 else pygame.Vector2(0, 0)

        if current_time - self.last_pick >= self.picking_time:
            self.can_pick = True
        if current_time - self.lastShot >= gunData['fire rate']:
            self.canShoot = True
        
        inSight = self.circle_rect_collision(self.sightRadius, self.world.player.rect)
        inRange = self.circle_rect_collision(self.innerRadius, self.world.player.rect)
        if inRange and self.canShoot:
            self.state = 'Shooting'
        elif inSight:
            self.state = 'Follow'
        else:
            self.state = 'Roam'

        if self.state == 'Follow':
            self.direction = direction
            self.strafe_timer += dt
            if self.strafe_timer >= 1.0:
                self.strafe_timer = 0
                self.strafe_dir *= -1

            strafe = pygame.math.Vector2(-direction.y, direction.x) * self.strafe_dir * 0.5

            if distance > desired_distance + 10:
                self.direction = (direction + strafe).normalize()
            elif distance < desired_distance - 10:
                self.direction = (-direction + strafe).normalize()
            else:
                self.direction = strafe.normalize() if strafe.length_squared() != 0 else pygame.math.Vector2(0, 0)

        elif self.state == 'Shooting':
            if self.canShoot:
                self.canShoot = False
                self.lastShot = current_time
                if self.gun.gunName == 'shotgun' or self.gun.gunName == 'sniper':
                    bulletSounds[random.randrange(0, 1)].play()
                else:
                    bulletSounds[random.randrange(2, 4)].play()
                for _ in range(gunData['bps']):
                    bullet = gun.Bullet(self.position, 'Enemy', to_player, self.world, gunData)
                    self.world.bullets.append(bullet)

        elif self.state == 'Roam':
            if self.can_pick:
                self.can_pick = False
                self.last_pick = current_time
                choice = random.randrange(1, 5)
                if choice in [1, 2]:
                    self.direction = direction
                else:
                    dir = pygame.math.Vector2(random.randrange(-10, 10), random.randrange(-10, 10))
                    if dir.length_squared() != 0:
                        self.direction = dir.normalize()
                    else:
                        self.direction = pygame.math.Vector2(1, 0)
        
        super().update(dt)
        

    def draw(self, window, offset):
        rotation_angle = math.sin(self.sway_time) * self.sway_amplitude
        rotated_sprite = pygame.transform.rotate(self.sprite, rotation_angle)
        window.blit(rotated_sprite, self.position - offset)
        self.gun.draw(window, offset)
        super().draw(window, offset)