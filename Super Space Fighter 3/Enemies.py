import pygame
from random import randint

def getVelocityToAPoint(posA: list, posB: list, speed: float)->list:
    """posA is the target object. posB is the subject thats moving towards the target. This function guarantees a constant speed while allowing for movement in any direction"""
    dx = abs(posB[0] - posA[0])
    dy = abs(posB[1] - posA[1])  
    
    try:
        gradient = dy/dx
    except ZeroDivisionError:
        gradient = 1e10 # assume very steep gradient when vertical
        
    velX = speed * (gradient**2 + 1)**-0.5
    velY = speed * (gradient**2 + 1)**-0.5 * gradient
    
    if posB[1] - posA[1] > 0:
        velY = -1*abs(velY) 
    if posB[0] - posA[0] > 0:
        velX = -1*abs(velX)
        
    return [velX, velY]
    
class EnemyList:
    """All enemy objects are part of an object from this class. Every frame, their update and render methods are called.
    Certain enemy-like classes have triggers for more enemy spawning. A tuple of the triggers
    are returned when update() is called.
    
    returned 0: this object was never meant to trigger anything
    returned (0, ...): this object is not currently triggering anything
    returned (str, ...): this object will trigger and gives a string so we know whats happening. The other variables are generally pos and then phase
    """
    def __init__(self):
        self.triggerList = []
        self.list = []

    
    def createEnemy(self, enemyType):
        self.list.append(enemyType)
        
    def update(self, listOfSprites: list):
        
        self.triggerList = [] # when iterating over each object, if a trigger is collected then it is kept here
        
        i = len(self.list) - 1
        while i >= 0:
            potentialTrigger = self.list[i].update(listOfSprites)
            
            if potentialTrigger != 0: # did the object return 0?
                if potentialTrigger[0] != 0: # if this object was made to send a trigger, is the first element in the return tuple a 0?
                    self.triggerList.append(potentialTrigger) # if neither are true, then we have to add to our trigger list
             
            if self.list[i].state == 0: # culls dead objects
                self.list.pop(i)
                i -= 1
            i -= 1
        
    def killAll(self):
        for i in range(len(self.list)):
            self.list[i].state = 0     
            
    def render(self, surf: pygame.Surface):
        for i in range(len(self.list)):
            self.list[i].render(surf)
            
    
        
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

class Missile:
    def __init__(self, playableArea: pygame.Rect, playerPos, initialPos: list[int] = [0,0], baseSpeed: int = 5):
        """spawns at initialPos and flies towards the playerPos in a straight line.
        
        Does not create a trigger for new enemy spawning"""
        
        # Image
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/missile1.png").convert(), (64,32))
        self.image1.set_colorkey((0,0,0))
        self.image2 = pygame.transform.scale(pygame.image.load("graphics/missile2.png").convert(), (64,32))
        self.image2.set_colorkey((0,0,0))
        self.image3 = pygame.transform.scale(pygame.image.load("graphics/missile3.png").convert(), (64,32))
        self.image3.set_colorkey((0,0,0))
        self.image4 = pygame.transform.scale(pygame.image.load("graphics/missile4.png").convert(), (64,32))
        self.image4.set_colorkey((0,0,0))
        self.FrameToImageDict = {
            0: self.image2,
            1: self.image3,
            2: self.image4,
            3: pygame.transform.flip(self.image3, False, True),
            4: pygame.transform.flip(self.image2, False, True),
            5: self.image1,
            6: self.image1,
            7: self.image1,
            8: self.image1,
            9: self.image1,
        }
        self.width, self.height = self.FrameToImageDict[0].get_width(), self.FrameToImageDict[0].get_height()
        self.currentImage = self.image1
        
        # Sound
        self.bulletSound = pygame.mixer.Sound("sound/sfx_wpn_cannon4.wav")
        self.bulletSound.set_volume(0.5)
        self.deathSound = pygame.mixer.Sound("sound/sfx_exp_various3.wav")
        self.deathSound.set_volume(0.5)
        self.bulletSound.play()
        
        self.pos = initialPos.copy()
        self.baseSpeed = baseSpeed
        self.vel = getVelocityToAPoint(playerPos, self.pos, self.baseSpeed)
        self.playableArea = playableArea
        self.state = 1 #active
        self.FramesSinceStart = 0
        
    def update(self, listOfSprites: list):
        """Completes kinematics, detects if object is offscreen (in which case it changes its state to a dead one ready to be killed by EnemyList), then completes mask collision
        detection with all of the player's bullets, known as listOfSprites, and finally the internal frame counter is updated."""
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 0 #dead
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 0 #dead
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 0 #dead
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 0 #dead
        
        
        self.mask = pygame.mask.from_surface(self.currentImage)
        for i in range(listOfSprites.getLen()):
            targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
            targetPos = listOfSprites.returnPosforIndex(i)
            
            offsetX = self.pos[0] - targetPos[0]
            offsetY = self.pos[1] - targetPos[1]
            
            if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                self.state = 0
                self.deathSound.play()
                break

        #image
        self.currentImage = self.FrameToImageDict[int(self.FramesSinceStart*0.2)%10]
 
        self.FramesSinceStart += 1
        return 0
        
    def render(self, surf: pygame.Surface):
        # int(self.FramesSinceStart*0.2)%10 is the formula that converts the frame counter to an index for which image is to be blitted
        surf.blit(self.currentImage, self.pos) 
              
class Bat:
    """spawns at initalPos and moves in a zigzag left/right.
        
        initialDirection: -1 for left and 1 for right
        
        Does not create a trigger for new enemy spawning"""
    def __init__(self, playableArea: pygame.Rect, initialDirection, initialPos: list[int], baseSpeed: int = 2):
        
        
        # Images
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/bat1.png").convert(), (48,48))
        self.image1.set_colorkey((0,0,0))
        self.image2 = pygame.transform.scale(pygame.image.load("graphics/bat2.png").convert(), (48,48))
        self.image2.set_colorkey((0,0,0))
        
        if initialDirection == 1: # corrects image for direction of motion
            self.image1 = pygame.transform.flip(self.image1, True, False)
            self.image2 = pygame.transform.flip(self.image2, True, False)
            initialPos[0] += 16
            
        self.FrameToImageDict = {
            0: self.image1,
            1: self.image2,
        }
            
        self.width = self.image1.get_width()
        self.height = self.image1.get_height()
        
        self.currentImage = self.image1
            
        # Sound
        self.deathSound = pygame.mixer.Sound("sound/sfx_deathscream_human4.wav")
        self.deathSound.set_volume(0.3)
        
        self.pos = initialPos.copy()
        self.baseSpeed = baseSpeed
        self.vel = [initialDirection*self.baseSpeed, self.baseSpeed]
        self.playableArea = playableArea
        self.state = 1 #active
        self.FramesSinceStart = 0
        
    def update(self, listOfSprites: list):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 0 #dead
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 0 #dead
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 0 #dead
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 0 #dead
        
        
        # collision detection with player bullets
        self.mask = pygame.mask.from_surface(self.currentImage)
        for i in range(listOfSprites.getLen()):
            targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
            targetPos = listOfSprites.returnPosforIndex(i)
            
            offsetX = self.pos[0] - targetPos[0]
            offsetY = self.pos[1] - targetPos[1]
            
            if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                self.state = 0
                self.deathSound.play()
                break

 
        
        
        # creates zig zag movement
        if self.FramesSinceStart % 20 == 0:
            self.vel[1] *= -1
            
        #image
        self.currentImage = self.FrameToImageDict[int(((self.FramesSinceStart%10)+5)*0.1)]
            
        self.FramesSinceStart += 1
        return 0
        
    def render(self, surf: pygame.Surface):
        # if self.FramesSinceStart % 10 >= 5:
        #     surf.blit(self.image1, self.pos)
        # else:
        #     surf.blit(self.image2, self.pos)
            
        surf.blit(self.currentImage, self.pos)
                
class Javelin:
    def __init__(self, playableArea: pygame.Rect, initialDirection, initialPos: list[int] = [0,0], baseSpeed: int = 6):
        """spawns at initalPos and moves fast.
        
        Does not die when in contact with bullets"""
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/javelin1.png").convert(), (96,16))
        self.image1.set_colorkey((0,0,0))
        self.image2 = pygame.transform.scale(pygame.image.load("graphics/javelin2.png").convert(), (96,16))
        self.image2.set_colorkey((0,0,0))
        
        if initialDirection == 1:
            self.image1 = pygame.transform.flip(self.image1, True, False)
            self.image2 = pygame.transform.flip(self.image2, True, False)
        self.currentImage = self.image1
        
        self.width, self.height = self.image1.get_width(), self.image1.get_height()
        
        self.pos = initialPos.copy()
        self.baseSpeed = baseSpeed
        self.vel = [initialDirection*self.baseSpeed, self.baseSpeed* 0.25]
        self.playableArea = playableArea
        self.state = 1 #active
        self.FramesSinceStart = 0
        
    def update(self, listOfSprites: list):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 0 #dead
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 0 #dead
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 0 #dead
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 0 #dead

        
        # creates zig zag movement
        if randint(1,30) == 13:
            self.vel[1] *= -1
            
        self.FramesSinceStart += 1
            
        return 0
        
    def render(self, surf: pygame.Surface):
        if self.FramesSinceStart % 10 >= 5:
            surf.blit(self.image1, self.pos)
        else:
            surf.blit(self.image2, self.pos)
    
class FlyBomb:
    """when shot this releases a number of randomly moving flies
    
    creates a trigger for new enemy spawning"""
    def __init__(self, playableArea: pygame.Rect, initialPos: list[int] = [0,0], baseSpeed: int = 2, direction: int = -1):
        
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/flybomb1.png").convert(), (64,64))
        self.image1.set_colorkey((0,0,0))
        self.currentImage = self.image1
        self.width, self.height = self.image1.get_width(), self.image1.get_height()
        
        
        self.explosionSound = pygame.mixer.Sound("sound/sfx_exp_odd3.wav")
        self.explosionSound.set_volume(0.8)
        
        self.playableArea = playableArea
        self.pA_RPoLW = [self.playableArea.left - 100, randint(self.playableArea.top, self.playableArea.bottom)] # Playable Area - Random Point on the Left Wall
        self.pA_RPoRW = [self.playableArea.right + 100, randint(self.playableArea.top, self.playableArea.bottom)] # Playable Area - Random Point on the Right Wall
        
        self.pos = initialPos.copy()
        self.direction = direction
        self.baseSpeed = baseSpeed
        if self.direction == -1:
            self.vel = getVelocityToAPoint(self.pA_RPoLW, self.pos, self.baseSpeed)
        else:
            self.vel = getVelocityToAPoint(self.pA_RPoRW, self.pos, self.baseSpeed)
        
        
        self.state = 1 #active
        self.lifespan = randint(120,300)
        self.trigger = 0
        
        
        self.FramesSinceStart = 0
        
    def update(self, listOfSprites: list):
        
        self.trigger = 0
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 0
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 0
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 0
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 0
            
        # collision detection with player bullets
        self.mask = pygame.mask.from_surface(self.currentImage)
        for i in range(listOfSprites.getLen()):
            targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
            targetPos = listOfSprites.returnPosforIndex(i)
            
            offsetX = self.pos[0] - targetPos[0]
            offsetY = self.pos[1] - targetPos[1]
            
            if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                self.state = 0
                break
        
        # state
            
        if self.FramesSinceStart == self.lifespan:
            self.state = 0
            
        if self.state == 0:
            self.trigger = "FlyBomb Explosion"
            self.explosionSound.play()

        self.FramesSinceStart += 1
        
        return (self.trigger, self.pos)
        
        
    def render(self, surf: pygame.Surface):
        if self.lifespan - self.FramesSinceStart < 60: # flicker warning of explosion
            if self.FramesSinceStart % 6 > 2:
                surf.blit(self.image1, self.pos)
        else:
            surf.blit(self.image1, self.pos)
    
class Fly:
    """spawned upon the explosion of a FlyBomb"""
    def __init__(self, playableArea: pygame.Rect, initialPos: list[int], baseSpeed: int = 1):
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/fly1.png").convert(), (32,32))
        self.image1.set_colorkey((0,0,0))
        self.image2 = pygame.transform.scale(pygame.image.load("graphics/fly2.png").convert(), (32,32))
        self.image2.set_colorkey((0,0,0))
        self.currentImage = self.image1
        self.width = self.image1.get_width()
        self.height = self.image1.get_height()
        
        
        self.baseSpeed = baseSpeed
        self.playableArea = playableArea
        
        
        self.pos = [initialPos[0] + randint(-10,26), initialPos[1] + randint(-10,26)]
        self.vel = getVelocityToAPoint((randint(self.playableArea.left,self.playableArea.right),randint(self.playableArea.top,self.playableArea.bottom)), self.pos, self.baseSpeed)
        self.state = 1 #active
        
        self.FramesSinceStart = 0
        self.pA_RPoLW = [self.playableArea.left - 100, randint(self.playableArea.top, self.playableArea.bottom)] # Playable Area - Random Point on the Left Wall
        
    def update(self, listOfSprites: list):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 0 #dead
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 0 #dead
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 0 #dead
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 0 #dead

        self.FramesSinceStart += 1
        
        return 0
    
    def render(self, surf: pygame.Surface):
        
        if self.FramesSinceStart % 10 >= 5:
            surf.blit(self.image1, self.pos)
        else:
            surf.blit(self.image2, self.pos)

class FlyProjectile(Fly):
    """Similar to the Fly except its initial pos and vel are given directly instead of randomly generated.
    Acts more like a simple bullet. Used for the level 4 boss"""
    def __init__(self, playableArea: pygame.Rect, initialPos: list[int] = [0, 0],initialVel: list[int] = [0,0], baseSpeed: int = 1):
        super().__init__(playableArea, initialPos, baseSpeed)
        self.vel = initialVel
        self.pos = initialPos
        
    def update(self, listOfSprites: list):
        return super().update(listOfSprites)
    
    def render(self, surf: pygame.Surface):
        return super().render(surf)

class Lakitu:
    """goes left and right and drops stones
    
    creates a trigger for new enemy spawning"""
    def __init__(self, playableArea: pygame.Rect, initialPos: list[int] = [0,0], baseSpeed: int = 4):
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/lakitu1.png").convert(), (64,64))
        self.image1.set_colorkey((0,0,0))
        self.currentImage = self.image1
        self.width = self.image1.get_width()
        self.height = self.image1.get_height()
        
        self.pos = initialPos.copy()
        self.hp = 10
        self.immunityTime = 30
        self.baseSpeed = baseSpeed
        self.vel = [0,0]
        self.playableArea = playableArea
        self.horizontalDirection = "left"
        self.pA_RPoLW = [self.playableArea.left - 100, randint(self.playableArea.top, self.playableArea.bottom)] # Playable Area - Random Point on the Left Wall
        self.state = 1 #active
        self.trigger = 0
        
        self.FramesSinceStart = 0
        
    def update(self, listOfSprites: list):
        
        # collision detection with player bullets
        self.trigger = 0
        
        self.mask = pygame.mask.from_surface(self.currentImage)
        if self.immunityTime == 0:
            for i in range(listOfSprites.getLen()):
                targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
                targetPos = listOfSprites.returnPosforIndex(i)
                
                offsetX = self.pos[0] - targetPos[0]
                offsetY = self.pos[1] - targetPos[1]
                
                if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                    self.hp -= 1
                    self.immunityTime = 30
                    break
        else:
            self.immunityTime -= 1
            

        
        
        # move
        
        if self.horizontalDirection == "right":
            self.pos[0] += self.baseSpeed
            if self.pos[0] > self.playableArea.right - 50 - self.width:
                self.horizontalDirection = "left"
                self.image1 = pygame.transform.flip(self.image1, True, False)
        
        else:
            self.pos[0] -= self.baseSpeed
            if self.pos[0] < self.playableArea.left + 50:
                self.horizontalDirection = "right"
                self.image1 = pygame.transform.flip(self.image1, True, False)
        
        self.FramesSinceStart += 1
        
        # state
        if self.hp <= 0:
            self.state = 0
            
        if self.FramesSinceStart % 120 == 119:
            self.trigger = "Lakitu Drop Stone"
            
            
        return (self.trigger, self.pos)
        
    def render(self, surf: pygame.Surface):

        surf.blit(self.image1, self.pos)
        
    def getCentrePos(self)->list:
        return [self.pos[0]+self.width*0.5,self.pos[1]+self.height*0.5]

class Stone:
    """spawns at initalPos and falls like a stone"""
    def __init__(self, playableArea: pygame.Rect, initialPos: list[int] = [0,0]):
        
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/stone1.png").convert(), (24,24))
        self.image1.set_colorkey((0,0,0))
        self.currentImage = self.image1
        self.width = self.image1.get_width()
        self.height = self.image1.get_height()
        
        self.bulletSound = pygame.mixer.Sound("sound/sfx_wpn_grenadewhistle1.wav")
        self.bulletSound.set_volume(0.2)
        self.bulletSound.play()
        
        self.pos = initialPos.copy()
        self.vel = [0,0]
        self.playableArea = playableArea
        self.state = 1 #active
        self.FramesSinceStart = 0
        
    def update(self, listOfSprites: list):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 0 #dead
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 0 #dead
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 0 #dead
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 0 #dead
        
        self.vel[1] += 0.5
        
        
        # collision detection with player bullets
        self.mask = pygame.mask.from_surface(self.currentImage)
        for i in range(listOfSprites.getLen()):
            targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
            targetPos = listOfSprites.returnPosforIndex(i)
            
            offsetX = self.pos[0] - targetPos[0]
            offsetY = self.pos[1] - targetPos[1]
            
            if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                self.state = 0
                break

 
        self.FramesSinceStart += 1
        
        return 0 
        
        
    def render(self, surf: pygame.Surface):
        surf.blit(self.image1, self.pos)

class SplittingBall:
    """creates a trigger"""
    def __init__(self, playableArea: pygame.Rect, playerPos, splitUpPhase, initialPos: list[int] = [0,0], baseSpeed: int = 2):
        self.image1 = pygame.Surface((64,64))
        self.image1 = pygame.image.load("graphics/ball1.png").convert()
        self.image1.set_colorkey((0,0,0))
        self.image2 = pygame.Surface((32,32))
        self.image2 = pygame.image.load("graphics/ball2.png").convert()
        self.image2.set_colorkey((0,0,0))
        self.image3 = pygame.Surface((24,24))
        self.image3 = pygame.image.load("graphics/ball3.png").convert()
        self.image3.set_colorkey((0,0,0))

        self.deathSound = pygame.mixer.Sound("sound/sfx_deathscream_human4.wav")
        self.deathSound.set_volume(0.3)
        
        self.pos = initialPos.copy()
        self.baseSpeed = baseSpeed
        self.vel = getVelocityToAPoint(playerPos, self.pos, self.baseSpeed)
        self.vel[0] += randint(-1,1) # adds random effect
        self.vel[1] += randint(-1,1)
        self.playableArea = playableArea
        self.state = 1 #active
        self.immunityTime = 1
        self.splitUpPhase = splitUpPhase
        self.trigger = 0
        
        if self.splitUpPhase == 1:
            self.currentImage = self.image1
            self.immunityTime = 30
            self.width, self.height = 64, 64
        elif self.splitUpPhase == 2:
            self.currentImage = self.image2
            self.width, self.height = 32, 32
        elif self.splitUpPhase == 3:
            self.currentImage = self.image3
            self.width, self.height = 24, 24
            
        

        self.FramesSinceStart = 0
        
    def update(self, listOfSprites: list):
        
        self.trigger = 0
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        # collision detection with edge of screen
        if self.FramesSinceStart > 90: # if spawning from offscreen we allow a grace period
            if self.pos[0] < self.playableArea.left:
                self.vel = getVelocityToAPoint([randint(self.playableArea.left + 50, self.playableArea.right - 50), randint(self.playableArea.top + 50, self.playableArea.bottom - 50)], self.pos, self.baseSpeed)
            if self.pos[0] > self.playableArea.right - self.width:
                self.vel = getVelocityToAPoint([randint(self.playableArea.left + 50, self.playableArea.right - 50), randint(self.playableArea.top + 50, self.playableArea.bottom - 50)], self.pos, self.baseSpeed)
            if self.pos[1] < self.playableArea.top:
                self.vel = getVelocityToAPoint([randint(self.playableArea.left + 50, self.playableArea.right - 50), randint(self.playableArea.top + 50, self.playableArea.bottom - 50)], self.pos, self.baseSpeed)
            if self.pos[1] > self.playableArea.bottom - self.height:
                self.vel = getVelocityToAPoint([randint(self.playableArea.left + 50, self.playableArea.right - 50), randint(self.playableArea.top + 50, self.playableArea.bottom - 50)], self.pos, self.baseSpeed)
            
        
        
        
        # collision detection with player bullets
        if self.FramesSinceStart > self.immunityTime:
            self.mask = pygame.mask.from_surface(self.currentImage)

            for i in range(listOfSprites.getLen()):
                targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
                targetPos = listOfSprites.returnPosforIndex(i)
                
                offsetX = self.pos[0] - targetPos[0]
                offsetY = self.pos[1] - targetPos[1]
                
                if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                    self.state = 0
                    self.deathSound.play()
                    self.splitUpPhase += 1
                    if self.splitUpPhase > 3:
                        self.trigger = 0
                    else:
                        self.trigger = "SplittingBall Split"
                    break

 
        self.FramesSinceStart += 1
        
        return (self.trigger, self.pos, self.splitUpPhase)
        
        
    def render(self, surf: pygame.Surface):
        surf.blit(self.currentImage, self.pos)
        
    def getCentrePos(self)->list:
        return [self.pos[0]+self.width*0.5,self.pos[1]+self.height*0.5]

class Boss(pygame.sprite.Sprite):
    def __init__(self, playableArea: pygame.Rect):
        self.image = pygame.Surface((64,64))
        self.image.fill(0xff0000)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.playableArea = playableArea
        
        self.pos = [playableArea.right - 100,200]
        self.newPos = [randint(self.playableArea.left + 10,self.playableArea.right - 10 - self.width), randint(self.playableArea.top + 10,self.playableArea.bottom - 10 -self.height)]
        self.vel = [0,0]
        self.baseSpeed = 5
        self.verticalDirection = "down"
        self.horizontalDirection = "left"
        self.triggeredFinalPush = False
        self.firstFrameofFight = True
        self.randomFrameCounter = randint(60,240)
        self.bossPhase = 0
        self.active = False
        self.visible = False
        self.immunityTime = 0
        self.invulnerable = False
        self.hpDict = {
            1: 8,
            2: 12,
            3: 12,
            4: 24,
            5: 12,
            
        }
        self.hp = self.hpDict[1]
        self.maxHp = self.hpDict[1]
        
        
        self.relativeBulletSpawnPos = [48,32]
        
        self.ComicSansFont = pygame.font.SysFont("Comic Sans", 20)
        self.myFont = pygame.font.Font("nintendo-font.ttf", 20)
        
        self.FramesSinceStart = 0
        
    def update(self, playerPos: list[int], bossType):
        """bossType should be the game level because there is one boss which changes behaviour based on 'bossType'"""
        self.bossType = bossType
        if self.active:
            if bossType == 1:
                # moves up and down at the right side of the screen

                if self.verticalDirection == "down":
                    self.pos[1] += self.baseSpeed
                    if self.pos[1] > self.playableArea.bottom - 50 - self.height:
                        self.verticalDirection = "up"
                
                else:
                    self.pos[1] -= self.baseSpeed
                    if self.pos[1] < self.playableArea.top + 50:
                        
                        self.verticalDirection = "down"
       
            elif bossType == 2:
                # teleports every 120 frames
                
                if self.FramesSinceStart % 120 == 90:
                    self.newPos = [randint(self.playableArea.left + 10,self.playableArea.right - 10 - self.width), randint(self.playableArea.top + 10,self.playableArea.bottom - 10 -self.height)]
                
                if self.FramesSinceStart % 120 == 119:
                    self.pos = self.newPos
                    
            elif bossType == 3:
                # moves left and right periodically
                self.baseSpeed = 8
                
                
                if self.randomFrameCounter <= 0:
                    self.randomFrameCounter = randint(60,240)
                    self.bossPhase = 1
                    if self.pos[0] > self.playableArea.centerx:
                        self.newPos = [self.playableArea.left + 10, self.pos[1]]
                    else:
                        self.newPos = [self.playableArea.right - 10 - self.width, self.pos[1]]

                if self.bossPhase == 0:

                    if self.verticalDirection == "down":
                        self.pos[1] += self.baseSpeed
                        if self.pos[1] > self.playableArea.bottom - 50 - self.height:
                            self.verticalDirection = "up"
                    
                    else:
                        self.pos[1] -= self.baseSpeed
                        if self.pos[1] < self.playableArea.top + 50:
                            
                            self.verticalDirection = "down"
                            
                    self.randomFrameCounter -= 1
                
                else:
                    
                    if abs(self.pos[0] - self.newPos[0]) > 20:
                        if self.pos[0] > self.newPos[0]:
                            self.pos[0] -= self.baseSpeed * 2
                        else:
                            self.pos[0] += self.baseSpeed * 2
                    else:
                        self.bossPhase = 0
                        
            elif bossType == 4:
                
                if self.FramesSinceStart == 120 and self.firstFrameofFight: # Behaviour for first frame of the fight
                    self.baseSpeed = 1 / (self.maxHp/self.hp)
                    self.pos = [randint(10,self.playableArea.right -10 - self.width),self.playableArea.top]
                    self.vel = [0,0]
                    self.bossPhase = 0
                    self.randomFrameCounter = randint(300,600)
                    self.firstFrameofFight = False
                    
                if self.bossPhase == 0: # Stays near the top and fires projectiles left/right/down
                    
                    
                    self.vel = [0,0]
                    self.baseSpeed = 2 / (self.hp/self.maxHp)
                    
                    if self.horizontalDirection == "right":
                        self.pos[0] += self.baseSpeed
                        if self.pos[0] > self.playableArea.right - 20 - self.width or randint(1,60) == 1:
                            self.horizontalDirection = "left"
                            
                    elif self.horizontalDirection == "left":
                        self.pos[0] -= self.baseSpeed
                        if self.pos[0] < self.playableArea.left + 20 or randint(1,60) == 1:
                            self.horizontalDirection = "right"
                
                elif self.bossPhase == 1:
                    
                    
                    
                    self.vel = getVelocityToAPoint(playerPos, self.getCentrePos(), 3)
                    
                    self.pos[0] += self.vel[0]
                    self.pos[1] += self.vel[1]
                
                if self.hp == 1 and not self.triggeredFinalPush:
                    self.FramesSinceStart = self.randomFrameCounter # creates a more interesting fight
                    self.triggeredFinalPush = True
                    self.invulnerable = True
                
                if self.FramesSinceStart >= self.randomFrameCounter:
                    if self.bossPhase == 1:  
                        if self.FramesSinceStart >= self.randomFrameCounter + 60:
                            self.pos = self.newPos
                            self.bossPhase = 0
                            self.invulnerable = True
                            self.FramesSinceStart = 0
                            self.randomFrameCounter = randint(240,600)
                        elif self.FramesSinceStart == self.randomFrameCounter:
                            self.newPos = [randint(10,self.playableArea.right -10 - self.width),self.playableArea.top]
                    else:
                        self.bossPhase = 1
                        self.invulnerable = False
                        self.randomFrameCounter = randint(300,600)
                        self.FramesSinceStart = 0
                    
                    
                
       

        self.FramesSinceStart += 1
        
    def render(self, surf: pygame.Surface):
        if self.visible:
            
            if self.bossType == 2 and self.FramesSinceStart % 120 > 90:
                # creates the flicker effect warning of an imminent teleport for the level 2 boss
                if self.FramesSinceStart % 6 >= 3:
                    surf.blit(self.image, self.newPos)
                else:
                    surf.blit(self.image, self.pos)
            
            elif self.bossType == 4 and self.FramesSinceStart > self.randomFrameCounter:
                # creates the flicker effect warning of an imminent teleport for the level 4 boss
                if self.FramesSinceStart % 6 >= 3:
                    surf.blit(self.image, self.newPos)
                else:
                    surf.blit(self.image, self.pos)
            
            else:
                
            
                surf.blit(self.image, self.pos)
        
        
    def renderStats(self, surf: pygame.Surface):
        """renders the boss health onto the status screen"""
        self.hpDrawY = 43
        self.hpDrawX = self.playableArea.right - 300
        for i in range(self.hp):
            if i % 12 == 0 and i != 0:
                self.hpDrawY += 20
            
            self.hpDrawX = self.playableArea.right - 300 + 20*(i%12)
            
            pygame.draw.circle(surf, 0xff0000, (self.hpDrawX, self.hpDrawY), 10)
            
        
            
        label = self.myFont.render("Boss", True, 0xffffff)
        surf.blit(label, (self.playableArea.right - 310,0))
    
        
    def getCentrePos(self)->list:
        return [self.pos[0]+self.width*0.5,self.pos[1]+self.height*0.5]
    
    def returnDeathState(self):
        if self.hp == 0:
            return True
        else:
            return False
        
    def doCollisionDetectionwithBullets(self, listOfSprites: list):
        self.mask = pygame.mask.from_surface(self.image)
        if self.invulnerable == False:
            if self.immunityTime == 0:
                for i in range(listOfSprites.getLen()):
                    targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
                    targetPos = listOfSprites.returnPosforIndex(i)
                    
                    offsetX = self.pos[0] - targetPos[0]
                    offsetY = self.pos[1] - targetPos[1]
                    
                    if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                        self.hp -= 1
                        self.immunityTime = 30
                        break
            else:
                self.immunityTime -= 1
    
# despite helping the player, powerups are known as "enemies" because they act very similar to one
class PowerupList:
    def __init__(self):
        self.list = []
        self.powerupCollected = 0
    
    def createEnemy(self, enemyType):
        self.list.append(enemyType)
        
    def update(self, listOfSprites: list, player):
        self.powerupCollected = 0
        i = len(self.list) - 1
        while i >= 0:
            self.list[i].update(listOfSprites, player)
            if self.list[i].pickedUp:
                self.powerupCollected = self.list[i].powerupType
            if self.list[i].state == 0:
                self.list.pop(i)
                i -= 1
            i -= 1
        
    def killAll(self):
        for i in range(len(self.list)):
            self.list[i].state = 0     
            
    def render(self, surf: pygame.Surface):
        for i in range(len(self.list)):
            self.list[i].render(surf)
            
        
    def getLen(self)->int:
        return len(self.list)
    
    def getIndex(self, index):
        return self.list[index]
    
    def returnRectforIndex(self, index):
        return self.list[index]
    
    def returnMaskforIndex(self, index):
        return pygame.mask.from_surface(self.list[index].image)
    
    def returnPosforIndex(self, index):
        return self.list[index].pos
    
class PowerUp:
    def __init__(self, playableArea: pygame.Rect, initialPos: list[int] = [0,0], baseSpeed: int = 2, powerupType: int = 1):
        """fall from the ceiling"""
        self.image1 = pygame.transform.scale(pygame.image.load("graphics/powerup1.png").convert(), (48,48))
        self.image1.set_colorkey((0,0,0))
        self.image = self.image1
        self.pickupSound = pygame.mixer.Sound("sound/sfx_sounds_fanfare1.wav")
        self.pickupSound.set_volume(0.5)
        self.deathSound = pygame.mixer.Sound("sound/sfx_sounds_damage1.wav")
        self.deathSound.set_volume(0.5)

        self.pos = initialPos.copy()
        self.baseSpeed = baseSpeed
        self.vel = [0,self.baseSpeed]
        self.playableArea = playableArea
        self.state = 1 #active
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.FramesSinceStart = 0
        self.powerupType = powerupType
        self.pickedUp = False
        
    def update(self, listOfSprites: list, player):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] < self.playableArea.left - self.width:
            self.state = 0 #dead
        if self.pos[0] > self.playableArea.right + 2*self.width:
            self.state = 0 #dead
        if self.pos[1] < self.playableArea.top - self.height:
            self.state = 0 #dead
        if self.pos[1] > self.playableArea.bottom + 2*self.height:
            self.state = 0 #dead
        
        
        # collision detection with player bullets
        self.mask = pygame.mask.from_surface(self.image)
        for i in range(listOfSprites.getLen()):
            targetMask: pygame.mask.Mask = listOfSprites.returnMaskforIndex(i)
            targetPos = listOfSprites.returnPosforIndex(i)
            
            offsetX = self.pos[0] - targetPos[0]
            offsetY = self.pos[1] - targetPos[1]
            
            if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
                self.state = 0
                self.deathSound.play()
                break

 
        
        
        # collision w player
        targetMask: pygame.mask.Mask = player.mask
        targetPos = player.pos.copy()
        
        offsetX = self.pos[0] - targetPos[0]
        offsetY = self.pos[1] - targetPos[1]
        
        if targetMask.overlap_area(self.mask, [offsetX, offsetY]) != 0:
            self.state = 0
            self.pickedUp = True
            self.pickupSound.play()
        
        self.FramesSinceStart += 1
        
        
    def render(self, surf: pygame.Surface):
        surf.blit(self.image1, self.pos)
