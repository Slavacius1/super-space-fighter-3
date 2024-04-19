from typing import Any
import pygame

class Explosion:
    """class to create and draw explosions onto the screen"""
    def __init__(self, pos: list, size: int) -> None:
        explosionTableImage = pygame.image.load("graphics/explosionTable.png").convert()
        explosionTableImage.set_colorkey((0,0,0))
        
        
        
        # extracts images from explosion Table and stores in a list
        explosionImages: list[pygame.Surface] = []
        if size == 1:
            explosionRowImage = explosionTableImage.subsurface((0,0), (234,30))
            for i in range(7):
                explosionImages.append(explosionRowImage.subsurface((34*i,0),(30,30)))
                
        elif size == 2:
            explosionRowImage = explosionTableImage.subsurface((1,39), (220,28))   
            for i in range(7):
                explosionImages.append(explosionRowImage.subsurface((32*i,0),(28,28)))
                
        elif size == 3:
            explosionRowImage = explosionTableImage.subsurface((3,75), (204,24))  
            for i in range(7):
                explosionImages.append(explosionRowImage.subsurface((30*i,0),(24,24))) 
                
        else:
            raise ValueError("sizes are 1, 2 or 3 only")
        
        self.imageList = explosionImages
        
        
        self.FramesSinceStart = 0
        self.state = 1
        
        self.rect = explosionImages[0].get_rect()
        self.rect.center = pos
        
    def update(self):
        self.FramesSinceStart += 1
        if self.FramesSinceStart == 7: # lifespan of 7 frames
            self.state = 0
            del self
            
        
        
    def render(self, surf: pygame.Surface):
        if self.state != 0:
            surf.blit(self.imageList[self.FramesSinceStart], self.rect.topleft)
            
        
        
    
    
        
        
        