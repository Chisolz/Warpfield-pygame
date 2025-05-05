import pygame
import random
import enemies
from StatStore import StatShop
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
        self.enemies = []
        self.bullets = []
        self.items = []
        self.player = None
        self.choice_time = 15000 # This is in ms
        self.chunk_update = None
        self.last_choice = 0
        self.can_choose = False
        self.spawn_time = 10000
        self.last_spawn = 0
        
        # Wave Attributes
        self.current_wave = 1
        self.wave_index = 5
        self.enemies_to_spawn = 6
        self.enemies_spawned = 0
        self.wave_active = True
        self.wave_cooldown = 7000
        self.last_wave = 0
        
        # Enemy spawn timer
        self.spawn_interval = 1000  # Time between enemy spawns (in ms)
        self.last_spawn_time = pygame.time.get_ticks()
        
        self.shop_open = False
        self.shop = None
        
    
    def cleanup(self):
        # Clear all sprite groups
        self.world_group.empty()
        
        # Clear all lists
        self.enemies.clear()
        self.bullets.clear()
        self.items.clear()
        
        # Clear world dictionary
        for chunk in self.world.values():
            chunk.cleanup()
        self.world.clear()
        
        # Clear references
        self.player = None
        self.shop = None
        self.world_group = None
        self.world = None
        self.chunk_update = None
        
    def initialize_shop(self, player):
        # Stat shop attributes
        self.shop_open = False
        self.shop = StatShop(player)
        
    
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
        
        for enemy in self.enemies:
            if enemy.killed:
                self.player.souls += 1
    
        # Update bullets, enemies, and items
        self.bullets = [bullet for bullet in self.bullets if not bullet.dead]
        self.enemies = [enemy for enemy in self.enemies if not enemy.dead]
        self.items = [item for item in self.items if not item.equipped]
    
        for bullet in self.bullets:
            bullet.update(dt)
        
        for item in self.items:
            item.update(dt)
        
        for enemy in self.enemies:
            enemy.update(dt)

        # Handle wave spawns
        if self.wave_active:
            # Spawn enemies at regular intervals
            if self.enemies_spawned < self.enemies_to_spawn and current_time - self.last_spawn_time >= self.spawn_interval:
                self.spawn_interval = random.randrange(1000, 8000)
                # Spawn an enemy
                idx = self.wave_index / 5
                enemy_levels = {
                    1: [enemies.Skeleboi],
                    2: [enemies.Skeleboi, enemies.DevilDare]
                }
                spawn_tiles = [tile for tile in self.world_group if not tile.collision]
                
                available_spawns = enemy_levels.get(idx)
                selected_enemy = random.choice(available_spawns)
                
                if spawn_tiles:
                    idx = random.randrange(0, len(spawn_tiles))
                    selected_tile = spawn_tiles[idx]
                    enemy = selected_enemy(self, selected_tile.position)
                    self.enemies.append(enemy)
                    self.enemies_spawned += 1
                    self.last_spawn_time = current_time

            # Check if the wave is complete
            if self.enemies_spawned == self.enemies_to_spawn and not self.enemies:
                self.wave_active = False
                self.last_wave_time = current_time
                self.shop.randomize_selected()
                self.shop_open = True

        # Start the next wave after cooldown and shop closing
        if not self.wave_active and current_time - self.last_wave >= self.wave_cooldown and not self.shop_open:
            self.current_wave += 1
            self.enemies_to_spawn += 2
            self.enemies_spawned = 0
            self.wave_active = True
            if self.current_wave > self.wave_index:
                self.wave_index += 5
            
            
        # Only allow choosing after the cooldown
        if current_time - self.last_choice >= self.choice_time:
            self.can_choose = True

        # Flag to track if player is found
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