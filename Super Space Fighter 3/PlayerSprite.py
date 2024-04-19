
import pygame
from math import floor
from random import randint

import pygame.image

def loadBulletImage(path: str):
    """loads a spritesheet of the bullets and seperates it so it can be accesed from a 2d array"""
    bulletTableImage = pygame.image.load(path).convert()
    bulletTableImage.set_colorkey((0,0,0))
    bulletTable = []
    
    for i in range(4):
        bulletTableRowImage = bulletTableImage.subsurface((0,10*i), (63,10))
        
        bulletTableRow = []
        bulletTableRow.append(pygame.transform.scale_by(bulletTableRowImage.subsurface((0,0), (11,10)),2))
        bulletTableRow.append(pygame.transform.scale_by(bulletTableRowImage.subsurface((11,0), (16,9)),2))
        bulletTableRow.append(pygame.transform.scale_by(bulletTableRowImage.subsurface((27,0), (17,9)),2))
        bulletTableRow.append(pygame.transform.scale_by(bulletTableRowImage.subsurface((44,0), (19,10)),2))
        bulletTable.append(bulletTableRow)
        
    return bulletTable
        
def generateRandomColour():
    return pygame.color.Color(randint(128,255),randint(128,255),randint(128,255))


class PlayerBulletList:
    def __init__(self):
        self.list = []
        
    def update(self, listOfSprites: list, boss, bossActive: bool):
        """listOfSprites refers to the sprites to check against. if the bullet collides w/ a sprite then it dies"""
        i = len(self.list) - 1
        while i >= 0:
            self.list[i].update(listOfSprites)
            if bossActive:
                self.list[i].doCollisionDetectionwithBoss(boss)
            i -= 1
    
    
            
        
    def deleteDeadBullets(self):
        i = len(self.list) - 1
        while i >= 0:
            if self.list[i].state == 0:
                self.list.pop(i)
                i -= 1
            i -= 1      
            
    def render(self, surf: pygame.Surface):
        for i in range(len(self.list)):
            self.list[i].render(surf)
            
    def createBullet(self, bulletType):
        self.list.append(bulletType)
        
    def getLen(self)->int:
        return len(self.list)
    
    def getIndex(self, index):
        return self.list[index]
    
    def returnRectforIndex(self, index):
        return self.list[index]
    
    def returnMaskforIndex(self, index):
        return pygame.mask.from_surface(self.list[index].currentImage)
    
    def returnPosforIndex(self, index):
        return self.list[index].pos

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, initialPos: list, initialDir: int, playableArea: pygame.Rect, bulletType: int):
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/bullet1.png").convert(), (20,4))
        self.image1.set_colorkey((0,0,0))
        self.currentImage = self.image1
        

        
        
        self.bulletImageTable = loadBulletImage("graphics/bulletTable.png")
        # Rows are the different colours
        # red, green, yellow and blue
        # Columns are the different sizes 
        # in increasing order.
        self.currentBulletTableRow = self.bulletImageTable[bulletType] # red
        self.bulletType = bulletType
        
        self.width = self.currentImage.get_width()
        self.height = self.currentImage.get_height()
        
        
        self.pos = initialPos.copy()
        self.dir = initialDir
        self.velX = initialDir
        
        self.playableArea = playableArea
        self.state = 2 #active
        self.FramesSinceStart = 0
        self.FramesLeftToLive = 1
        
        
    def update(self, listOfSprites):
        """listOfSprites refers to the sprites to check against. if the bullet collides w/ a sprite then it dies"""
        
        #decides image based on speed
        if abs(self.velX) <= 6:
            self.currentImage = self.currentBulletTableRow[0] # smallest bullet
        elif abs(self.velX) <= 12:
            self.currentImage = self.currentBulletTableRow[1] # smaller bullet
        elif abs(self.velX) <= 18:
            self.currentImage = self.currentBulletTableRow[2] # bigger bullet
        elif abs(self.velX) <= 24:
            self.currentImage = self.currentBulletTableRow[3] # biggest bullet
        self.width = self.currentImage.get_width()
        self.height = self.currentImage.get_height()
        
        if self.dir == -1:
            self.currentImage = pygame.transform.flip(self.currentImage, True, False)
        
        # Kinematics
        self.pos[0] += self.velX
        
        if self.bulletType == 1:
            self.velX = max(min(self.velX + 4 * self.dir, 60),-60) # limits velocity to 60 frames/second for hi speed bullets
        else:
            self.velX = max(min(self.velX + self.dir, 30),-30) # limits velocity to 30 frames/second
        
        # Culling offscreen bullets
        # Bullets wait a frame to die so enemies can detect collision
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 1 #one frame left of life
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 1 #one frame left of life
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 1 #one frame left of life
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 1 #one frame left of life
        
        # Collision detection
        if self.bulletType != 2:
            self.mask = pygame.mask.from_surface(self.currentImage)
            for i in range(listOfSprites.getLen()):
                targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
                targetPos = listOfSprites.returnPosforIndex(i)
                
                offsetX = self.pos[0] - targetPos[0]
                offsetY = self.pos[1] - targetPos[1]
                
                if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                    self.state = 1 #one frame left of life
                    break
        
        # frame counter  
        if self.state == 1:
            if self.FramesLeftToLive == 0:
                self.state = 0
            else:
                self.FramesLeftToLive -= 1
        
        self.FramesSinceStart += 1
        
    
    def doCollisionDetectionwithBoss(self, boss):
        """Runs collision detection with 1 sprite"""
        self.mask = pygame.mask.from_surface(self.currentImage)
        targetMask: pygame.mask.Mask = pygame.mask.from_surface(boss.image)
        targetPos = boss.pos
        
        offsetX = self.pos[0] - targetPos[0]
        offsetY = self.pos[1] - targetPos[1]
        
        if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
            self.state = 1
        
    def render(self, surf: pygame.Surface):
        if self.state == 2:
            surf.blit(self.currentImage, self.pos)
        
class Player(pygame.sprite.Sprite):
    def __init__(self, playableArea: pygame.Rect, playerBulletList: PlayerBulletList):
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/player1.png").convert(), (64,64))
        self.image1.set_colorkey((0,0,0))
        self.currentImage = self.image1
        self.width = self.image1.get_width()
        self.height = self.image1.get_height()
        
        self.mask = pygame.mask.from_surface(self.currentImage)
        
        
        self.bulletSound = pygame.mixer.Sound("sound/sfx_wpn_cannon4.wav")
        self.bulletSound.set_volume(0.2)
        self.lowhealthSound = pygame.mixer.Sound("sound/sfx_lowhealth_alarmloop3.wav")
        self.lowhealthSound.set_volume(0.3)
        self.damageSound = pygame.mixer.Sound("sound/sfx_damage_hit7.wav")
        self.damageSound.set_volume(0.3)
        
        self.pos = [10,playableArea.height*0.5+playableArea.top]
        self.vel = [0,0]
        self.baseSpeed = 8
        self.baseAcceleration = 2
        self.facingDirection = 1 # 1 for right, -1 for left
        self.hp = 8
        self.immunityTime = 0
        self.FramesSinceLastBullet = 0
        self.bulletType = 0
        self.randomColour = generateRandomColour()
        self.bulletTypeDescriptionDict = {
            0: ("standard", (255,0,0)),
            1: ("hi speed", (0,255,0)),
            2: ("piercing", (255,255,0)),
            3: ("multi shot", self.randomColour),
        }

        
        self.playableArea = playableArea
        
        self.bulletList = playerBulletList
        
        
        self.ComicSansFont = pygame.font.SysFont("Comic Sans", 20)
        self.myFont = pygame.font.Font("nintendo-font.ttf", 20)
        
        self.FramesSinceStart = 0
        
        
        self.visible = True
        
        #control logic
        self.RSHIFTDown = False
        
        
    
    def handleInputs(self):
        self.keys = pygame.key.get_pressed()
        # if self.keys[pygame.K_w]:
        #     self.vel[1] = -self.baseSpeed
        # elif self.keys[pygame.K_s]:
        #     self.vel[1] = self.baseSpeed
        # else:
        #     self.vel[1] = 0
            
        # if self.keys[pygame.K_a]:
        #     self.vel[0] = -self.baseSpeed
        # elif self.keys[pygame.K_d]:
        #     self.vel[0] = self.baseSpeed
        # else:
        #     self.vel[0] = 0
            
        if self.keys[pygame.K_w]:
            self.vel[1] = min(max(self.vel[1]-self.baseAcceleration,-self.baseSpeed),self.baseSpeed)
        elif self.keys[pygame.K_s]:
            self.vel[1] = min(max(self.vel[1]+self.baseAcceleration,-self.baseSpeed),self.baseSpeed)
        else:
            self.vel[1] = min(max(self.vel[1]*0.5,-self.baseSpeed),self.baseSpeed)
            if abs(self.vel[1]) <= 0.1:
                self.vel[1] = 0
            
        if self.keys[pygame.K_a]:
            self.vel[0] = min(max(self.vel[0]-self.baseAcceleration,-self.baseSpeed),self.baseSpeed)
        elif self.keys[pygame.K_d]:
            self.vel[0] = min(max(self.vel[0]+self.baseAcceleration,-self.baseSpeed),self.baseSpeed)
        else:
            self.vel[0] = min(max(self.vel[0]*0.5,-self.baseSpeed),self.baseSpeed)
            if abs(self.vel[0]) <= 0.1:
                self.vel[0] = 0
            
        if self.keys[pygame.K_RETURN]: #fire button
            if self.FramesSinceLastBullet > 16:
                self.bulletSound.play()
                if self.facingDirection == 1:
                    self.posOfBulletSpawn = [self.pos[0] + self.width - 6,
                                            self.pos[1] + self.height*.5 - 10]
                    
                    #extra positions for multishot
                    self.posOfBulletSpawn2 = [self.pos[0] + self.width - 12,
                                            self.pos[1] + self.height*.5 - 34]
                    self.posOfBulletSpawn3 = [self.pos[0] + self.width - 12,
                                            self.pos[1] + self.height*.5 + 14]
                else:
                    self.posOfBulletSpawn = [self.pos[0] - 10,
                                            self.pos[1] + self.height*.5 - 10]
                    
                    #extra positions for multishot
                    self.posOfBulletSpawn2 = [self.pos[0] - 4,
                                            self.pos[1] + self.height*.5 - 34]
                    self.posOfBulletSpawn3 = [self.pos[0] - 4,
                                            self.pos[1] + self.height*.5 + 14]
                if self.bulletType == 3:
                    
                    self.bulletList.createBullet(PlayerBullet(self.posOfBulletSpawn, self.facingDirection, self.playableArea, self.bulletType))
                    self.bulletList.createBullet(PlayerBullet(self.posOfBulletSpawn2, self.facingDirection, self.playableArea, self.bulletType))
                    self.bulletList.createBullet(PlayerBullet(self.posOfBulletSpawn3, self.facingDirection, self.playableArea, self.bulletType))
                    
                else:
                    self.bulletList.createBullet(PlayerBullet(self.posOfBulletSpawn, self.facingDirection, self.playableArea, self.bulletType))
                
                self.FramesSinceLastBullet = 0
                if self.bulletType == 1:
                    self.FramesSinceLastBullet = 4
                
        if self.keys[pygame.K_RSHIFT] and not self.RSHIFTDown: # flip button
            if self.facingDirection == -1:
                self.facingDirection = 1
                self.currentImage = pygame.transform.flip(self.currentImage, True, False)
            else:
                self.facingDirection = -1
                self.currentImage = pygame.transform.flip(self.currentImage, True, False)
            self.RSHIFTDown = True
        elif not self.keys[pygame.K_RSHIFT] and self.RSHIFTDown:
            self.RSHIFTDown = False
        
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.mask = pygame.mask.from_surface(self.currentImage)

        
        # collision detection
        if self.pos[0] < self.playableArea.left:
            self.pos[0] -= self.vel[0]
            self.pos[0] = self.playableArea.left
        if self.pos[0] + self.width > self.playableArea.right:
            self.pos[0] -= self.vel[0]
            self.pos[0] = self.playableArea.right - self.width
        if self.pos[1] < self.playableArea.top:
            self.pos[1] -= self.vel[1]
            self.pos[1] = self.playableArea.top
        if self.pos[1] + self.height > self.playableArea.bottom:
            self.pos[1] -= self.vel[1]
            self.pos[1] = self.playableArea.bottom - self.height
            
        
        
        if self.immunityTime % 6 > 2:
            self.visible = False
        else:
            self.visible = True
             
        if self.hp > 36:
            self.hp == 36
        if self.hp == 1 and self.FramesSinceStart % 60 == 1:
            self.lowhealthSound.play()
            
        # colour
        self.randomColour = generateRandomColour()
        self.bulletTypeDescriptionDict = {
            0: ("standard", (255,0,0)),
            1: ("hi speed", (0,255,0)),
            2: ("piercing", (255,255,0)),
            3: ("multi shot", self.randomColour),
        }
            
        self.FramesSinceStart += 1
        self.FramesSinceLastBullet += 1
        
    def render(self, surf: pygame.Surface):
        if self.visible:
            surf.blit(self.currentImage, self.pos)
        
        self.hpDrawY = 43
        self.hpDrawX = 15
        for i in range(self.hp):
            if i % 12 == 0 and i != 0:
                self.hpDrawY += 20
            
            self.hpDrawX = 15 + 20*(i%12)
            
            pygame.draw.circle(surf, 0xff0000, (self.hpDrawX, self.hpDrawY), 10)
            
        label = self.myFont.render("Player", True, 0xffffff)
        surf.blit(label, (8,0))
        
        if self.hp == 1 and self.FramesSinceStart % 60 > 29:
            self.label = self.myFont.render("low health!", True, (255,0,0))
            surf.blit(self.label, (400,60))
            
        label = self.myFont.render("bullet type:", True, self.bulletTypeDescriptionDict[self.bulletType][1])
        surf.blit(label, (640,0))
        label = self.myFont.render(self.bulletTypeDescriptionDict[self.bulletType][0], True, self.bulletTypeDescriptionDict[self.bulletType][1])
        surf.blit(label, (640,30))
        
        
        
    def getCentrePos(self)->list:
        return [self.pos[0]+self.width*0.5,self.pos[1]+self.height*0.5]
    
    def doCollisionDetectionwithEnemies(self, listOfSprites: list):
        """runs collision detection with a list of sprites"""
        if self.immunityTime == 0:
            for i in range(listOfSprites.getLen()):
                targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
                targetPos = listOfSprites.returnPosforIndex(i)
                
                offsetX = self.pos[0] - targetPos[0]
                offsetY = self.pos[1] - targetPos[1]
                
                if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                    self.hp -= 1
                    self.immunityTime = 30
                    self.damageSound.play()
                    break
        else:
            self.immunityTime -= 1
            
    def doCollisionDetectionwithBoss(self, boss):
        """Runs collision detection with 1 sprite"""
        if self.immunityTime == 0:
            targetMask: pygame.mask.Mask = pygame.mask.from_surface(boss.image)
            targetPos = boss.pos
            
            offsetX = self.pos[0] - targetPos[0]
            offsetY = self.pos[1] - targetPos[1]
            
            if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                self.hp -= 1
                self.immunityTime = 30
                self.damageSound.play()
        else:
            self.immunityTime -= 1
        
    def returnDeathState(self):
        if self.hp == 0:
            return True
        else:
            return False
            
