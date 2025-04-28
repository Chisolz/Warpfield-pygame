import pygame
import json

class Spritesheet:
    def __init__(self, fileName):
        self.fileName = fileName
        self.spriteSheet = pygame.image.load(fileName).convert()
        self.metaData = self.fileName.replace('.png', '.json')
        with open(self.metaData) as f:
            self.data = json.load(f)
        f.close()
    
    
    def getSprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.spriteSheet, (0, 0), (x, y, width, height))
        return sprite
    
    
    def parseSprite(self, name):
        sprite = self.data['frames'][name]['frame']
        x, y, w, h = sprite['x'], sprite['y'], sprite['w'], sprite['h']
        image = self.getSprite(x, y, w, h)
        return image


class Tilemap(Spritesheet):
    def __init__(self, fileName):
        super().__init__(fileName)
        self.images = []
        self.tileProperties = {}
        tileMetaData = self.fileName.replace('.png', '.tda')
        with open(tileMetaData) as f:
            self.tileData = json.load(f)
        f.close()
        
        for i in self.data['frames']:
            self.parseTile(i)
            if int(i) < len(self.tileData['tiles']):
                for tile in self.tileData['tiles']:
                    tile_id = tile['id']
                    if 'properties' in tile:
                        self.tileProperties[tile_id] = tile['properties']
        
    
    def parseTile(self, id):
        image = super().parseSprite(str(id))
        self.images.append(image)
