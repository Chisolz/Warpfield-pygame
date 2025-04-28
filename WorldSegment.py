import pygame
import json
from pathlib import Path
from tile import Tile


class Chunk:
    def __init__(self, corner, chunkPos, group, scale):
        self.corner = corner
        self.position = chunkPos
        self.world_group = group
        self.scale = scale
        self.hasPlayer = False
        self.chunks = {}
        presets = Path('Dungeon Assets/Dungeon Presets') # Folder with preset chunks
        for file in presets.iterdir():
            if file.is_file():
                if file.name.startswith(corner): # Check if the file name starts with the chunk corner
                    fileName = file.name.removesuffix('.json')
                    name = fileName.removeprefix(corner)
                    data = None
                    with open(file) as f:
                        data = json.load(f)
                    f.close()
                    self.chunks[name] = data
    
    
        # Store the width and height of both the chunk and tiles
        self.chunkWidth = self.chunks['1']['width'] 
        self.chunkHeight = self.chunks['1']['height']
        self.tileWidth = self.chunks['1']['tilewidth']
        self.tileHeight = self.chunks['1']['tileheight']
        self.selectedChunk = []
        self.selectChunk(1)
        
        # Store the rect for the chunk
        width = self.chunks['1']['layers'][1]['objects'][0]['width'] * scale
        height = self.chunks['1']['layers'][1]['objects'][0]['height'] * scale
        self.rect = pygame.Rect(chunkPos.x, chunkPos.y, width, height)
    
    
    def selectChunk(self, chunkNum):
        for tile in self.selectedChunk:
            self.world_group.remove(tile)
        self.selectedChunk.clear()
        
        selected = self.chunks[str(chunkNum)]
        tileWidth = selected['tilewidth']
        tileHeight = selected['tileheight']
        
        for layer in selected['layers']:
            if layer['type'] == 'tilelayer':
                data = layer['data']
                chunkWidth = layer['width']
                chunkHeight = layer['height']
                
                for y in range(chunkHeight):
                    for x in range(chunkWidth):
                        index = y * chunkWidth + x
                        tile_id = data[index]
                        
                        if tile_id > 0:
                            tile_x = x * tileWidth
                            tile_y = y * tileHeight
                            tilePos = pygame.math.Vector2(tile_x, tile_y) * self.scale
                            
                            relativePos = tilePos + self.position * self.scale

                            tile = Tile(relativePos, self.world_group)
                            tile.set_current(tile_id - 1)
                            self.selectedChunk.append(tile)
