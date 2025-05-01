import pygame
import random
import enemies
from tile import Tile
from WorldSegment import Chunk

presetFolder = 'Dungeon Assets/Dungeon Presets'

class World:
    def __init__(self):
        self.scale = 3
        self.debug = False
        self.tr_origin = None
        self.tl_origin = None
        self.br_origin = None
        self.bl_origin = None
        self.world_group = pygame.sprite.Group()
        self.world = self.initialize_world()
        self.enemies = [enemies.Skeleboi(self, pygame.math.Vector2(500, 500))]
        self.bullets = []
        self.items = []
        self.player = None
        self.choice_time = 15000 # This is in ms
        self.chunk_update = None
        self.last_choice = 0
        self.can_choose = False
        self.spawn_time = 10000
        self.last_spawn = 0
        
        
    
    def initialize_world(self):
        
        # Initialize top left chunk
        self.tl_origin = pygame.math.Vector2()
        topleft = Chunk('TL', self.tl_origin, self.world_group, self.scale)
        
        # Get chunk height and width since all the same
        chunkWidth = topleft.chunkWidth * topleft.tileWidth
        chunkHeight = topleft.chunkHeight * topleft.tileHeight
        
        # Initialize top right chunk
        self.tr_origin = pygame.math.Vector2(chunkWidth, 0)
        topright = Chunk('TR', self.tr_origin, self.world_group, self.scale)
        
        # Initialize bottom left chunk
        self.bl_origin = pygame.math.Vector2(0, chunkHeight)
        bottomleft = Chunk('BL', self.bl_origin, self.world_group, self.scale)
        
        # Initialize bottom right chunk
        self.br_origin = pygame.math.Vector2(chunkWidth, chunkHeight)
        bottomright = Chunk('BR', self.br_origin, self.world_group, self.scale)
        
        world = {
            'top left': topleft,
            'top right': topright,
            'bottom left': bottomleft,
            'bottom right': bottomright
        }

        return world
    
    
    def update(self, dt):
        current_time = pygame.time.get_ticks()
    
        # Update bullets and enemies
        self.bullets = [bullet for bullet in self.bullets if not bullet.dead]
        self.enemies = [enemy for enemy in self.enemies if not enemy.dead]
        self.items = [item for item in self.items if not item.equipped]
    
        for bullet in self.bullets:
            bullet.update(dt)
        
        for item in self.items:
            item.update(dt)
        
        for enemy in self.enemies:
            enemy.update(dt)

        
        if current_time - self.spawn_time >= self.last_spawn:
            self.last_spawn = current_time
            spawnTiles = [tile for tile in self.world_group if not tile.collision]
            idx = random.randrange(0, len(spawnTiles) - 1)
            selected_tile = spawnTiles[idx]
            enemy = enemies.Skeleboi(self, selected_tile.position)
            self.enemies.append(enemy)
        
        # Only allow choosing after the cooldown
        if current_time - self.last_choice >= self.choice_time:
            self.can_choose = True

        # Flag to track if we already found where player is
        player_in_chunk = False
    
        for chunk in self.world.values():
            if chunk.rect.colliderect(self.player.rect):
                chunk.hasPlayer = True
                player_in_chunk = True
            else:
                chunk.hasPlayer = False

        # Only do heavy world randomization if player is in *some* chunk
        if self.can_choose and player_in_chunk:
            empty_chunks = [chunk for chunk in self.world.values() if not chunk.hasPlayer]
            if empty_chunks:
                selected_chunk = random.choice(empty_chunks)
                self.chunk_update = (selected_chunk, random.randint(1, 4))
                self.can_choose = False
            self.last_choice = current_time

    
    def draw(self, offset):
        surface = pygame.display.get_surface()
        
        for chunk in self.world.values():
            for tile in chunk.selectedChunk:
                tile.draw(surface, offset)
        
        for bullet in self.bullets:
            bullet.draw(surface, offset)
        
        for item in self.items:
            item.draw(offset)
    
        for enemy in self.enemies:
            enemy.draw(surface, offset)

        if self.chunk_update:
            chunk, preset_id = self.chunk_update
            chunk.selectChunk(preset_id)
            self.world[chunk.corner] = chunk
            self.chunk_update = None
        
        if self.debug:
            for chunk in self.world.values():
                for tile in chunk.selectedChunk:
                    if tile.collision:
                        pygame.draw.rect(surface, 'blue', tile.rect.move(-offset))