import pygame
import random
import math
import gun

class Enemy:
    def __init__(self, world, hp, scale, sightRadius):
        self.world = world
        self.flipped = False
        self.position = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(0, 0)
        self.state = None
        self.sightRadius = sightRadius
        self.innerRadius = sightRadius - 50
        self.moving = False
        self.scale = scale
        self.dead = False
        self.speed = 100
        self.new_pos = self.position.copy()
        self.health = hp
        self.picking_time = 5000
        self.strafe_timer = 0
        self.strafe_dir = 1
        self.sway_amplitude = 10
        self.sway_speed = 10
        self.sway_time = 0
        self.offset_x = None
        self.canShoot = True
        self.lastShot = 0
        self.gun = gun.Gun()
        self.gun.select_gun('smg')
        self.rect = pygame.Rect(self.position.x, self.position.y, 50, 50)

    def update(self, dt):
        # Check if hit by bullet
        for bullet in self.world.bullets:
            if self.rect.colliderect(bullet.rect) and bullet.shotBy == 'Player':
                bullet.dead = True
                self.health -= bullet.damage

        if self.health <= 0:
            self.dead = True

        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()

        if self.direction.x < 0:
            self.flipped = True
        else:
            self.flipped = False

        move = self.direction * self.speed * dt
        new_position = self.position + move
        new_position = self.resolve_collisions(new_position)

        self.sway_time += dt * self.sway_speed
        self.offset_x = math.sin(self.sway_time) * self.sway_amplitude

        self.gun.Eupdate(self.position, -self.direction)

        self.position = new_position
        self.rect.topleft = (self.position.x, self.position.y)

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

    def draw(self, window, offset):
        pass


class Skeleboi(Enemy):
    def __init__(self, world, position):
        super().__init__(world, 150, 3, 250)
        sprite = pygame.image.load('Assets/Enemies/SkeleBoy.png').convert()
        w, h = sprite.get_width(), sprite.get_height()
        sprite.set_colorkey((0, 0, 0))
        self.sprite = pygame.transform.scale(sprite, (w * self.scale, h * self.scale))
        self.spriteFlipped = pygame.transform.flip(self.sprite, True, False)
        self.rect = pygame.Rect(position.x, position.y, self.sprite.get_width(), self.sprite.get_height())
        self.position = position.copy()
        self.rect.topleft = position
        self.last_pick = 0
        self.can_pick = True
        self.new_pos = self.position.copy()

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
        selectedSprite = self.spriteFlipped if self.flipped else self.sprite
        rotation_angle = math.sin(self.sway_time) * self.sway_amplitude
        rotated_sprite = pygame.transform.rotate(selectedSprite, rotation_angle)
        window.blit(rotated_sprite, self.position - offset)
        self.gun.draw(window, offset)

        # Draw collision box
        #pygame.draw.rect(window, 'red', self.rect.move(-offset))
        
        
        # Draw sight radii
        #pygame.draw.circle(window, 'blue', self.position - offset, self.sightRadius)
        #pygame.draw.circle(window, 'yellow', self.position - offset, self.innerRadius)
