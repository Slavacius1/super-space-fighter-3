import pygame
from random import randint
import GameSettings
from Mode7.mode7 import Mode7
import math

class gameClass:
    def __init__(self):
        pygame.init()
        self.screenX = GameSettings.RESOLUTION[0] 
        self.screenY = GameSettings.RESOLUTION[1] 
        self.screen = pygame.display.set_mode(GameSettings.RESOLUTION, GameSettings.FLAGS)
        pygame.display.set_caption("Super Space Fighter 3 indev")
        self.screenRect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.state = 1 #title
        self.level = 1
        self.powerupTimer = randint(1,1200)
        self.score = 0
        self.previousFrameState = 1
        self.FramesSinceStart = 0
        
        self.mode7 = Mode7(self, "Mode7/textures/grass2.png", "Mode7/textures/ceil_2.png", 0, 50)

        self.mode7.speed = 0.01
        
        pygame.mixer.init()
        
        self.gameoverSound = pygame.mixer.Sound("sound/sfx_sounds_impact9.wav")
        self.gameoverSound.set_volume(1)
        
        
        self.playableArea = pygame.rect.Rect(0,100,self.screenX,self.screenY-100)
        # rect points created for convenience
        self.pAMidBottom = list(self.playableArea.midbottom)
        self.pAMidTop = list(self.playableArea.midtop)
        self.pA_RPoRW = [self.playableArea.right, randint(self.playableArea.top + 50, self.playableArea.bottom - 50)] # Playable Area - Random Point on the Right Wall
        self.pA_RPoLW = [self.playableArea.left, randint(self.playableArea.top + 50, self.playableArea.bottom - 50)] # Playable Area - Random Point on the Left Wall
        self.pA_RP = [randint(self.playableArea.left + 50, self.playableArea.right - 50), randint(self.playableArea.top + 50, self.playableArea.bottom - 50)] # Playable Area - Random Point
        
        self.statusArea = pygame.rect.Rect(0,0,self.screenX,100)
        self.progressBarRectBackground = pygame.rect.Rect(10, self.statusArea.bottom - 10, self.statusArea.width - 20, 5)
        
        self.ComicSansFont = pygame.font.SysFont("Comic Sans", 20)
        self.myFont = pygame.font.Font("nintendo-font.ttf", 20)
        self.myFontBig = pygame.font.Font("nintendo-font.ttf", 32)
        
        self.levelLengthsDict = { # lengths of each level before boss in frames
            1: 1200,
            2: 1200,
            3: 1800, #1800
            4: 2700, #2700 default
            5: 2900,
        }
        
        pygame.mixer.music.load("music\Juhani Junkala [Retro Game Music Pack] Title Screen.wav"),
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)
        
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = 0
                
    def handleInputs(self):
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_ESCAPE]:
            self.state = 0
            
        if self.state == 1: 
            if 1 in self.keys: # any key down
                self.state = 2
                pygame.mixer.music.fadeout(1000)
            if self.keys[pygame.K_1]:
                self.level = 1
            elif self.keys[pygame.K_2]:
                self.level = 2
            elif self.keys[pygame.K_3]:
                self.level = 3
            elif self.keys[pygame.K_4]:
                self.level = 4
            elif self.keys[pygame.K_5]:
                self.level = 5
            
                
                
            
    def update(self):
        """computes logic to do with game state"""
        self.FramesSinceStart += 1
        
        if self.state != self.previousFrameState: #state has changed so reset frame counter
            self.FramesSinceStart = 0
            
        self.previousFrameState = self.state
        
        if self.state == 2 and self.FramesSinceStart > 60: # frame timer on level begin screen
            self.state = 3
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            if self.level == 1:
                pygame.mixer.music.load("music\Juhani Junkala [Retro Game Music Pack] Level 1.wav")
            elif self.level == 2:
                pygame.mixer.music.load("music\Juhani Junkala [Retro Game Music Pack] Level 2.wav")
            elif self.level == 3:
                pygame.mixer.music.load("music\Juhani Junkala [Retro Game Music Pack] Level 3.wav")
            elif self.level == 4:
                pygame.mixer.music.load("music\Juhani Junkala [Retro Game Music Pack] Level 1.wav")
            elif self.level == 5:
                pygame.mixer.music.load("music\Juhani Junkala [Retro Game Music Pack] Level 2.wav")
            pygame.mixer.music.play(-1)
        elif self.state == 2 and self.FramesSinceStart < 60:
            self.mode7.angle = 3.141592654 * (self.FramesSinceStart/59)
            
            
        elif self.state == 3 and self.FramesSinceStart > self.levelLengthsDict[self.level]:
            self.state = 4
            
        elif self.state == 5 and self.FramesSinceStart > 180:
            self.state = 0
            
        elif self.state == 6 and self.FramesSinceStart > 180:
            self.state = 2
            self.level += 1
            self.mode7.speed += 0.005
            self.powerupTimer = randint(1,self.levelLengthsDict[self.level]-400)
            if self.level == 4:
                self.resetMode7("Mode7/textures/seamless space.PNG", "Mode7/textures/seamless space.PNG", fogMode=1)
            
        self.pA_RPoRW = [self.playableArea.right, randint(self.playableArea.top + 5, self.playableArea.bottom - 5)] # Playable Area - Random Point on the Right Wall
        self.pA_RPoLW = [self.playableArea.left-64, randint(self.playableArea.top + 5, self.playableArea.bottom - 5)] # Playable Area - Random Point on the Left Wall
        self.pA_RP = [randint(self.playableArea.left + 50, self.playableArea.right - 50), randint(self.playableArea.top + 50, self.playableArea.bottom - 50)] # Playable Area - Random Point
        
        self.mode7.update()
        self.mode7.alt = 2 + 0.2*math.cos(self.FramesSinceStart*0.01)
        
            
        
            
        
            
    def renderBackground(self, bossHp=8, bossMaxHp=8):
        
        
        self.screen.fill(0x000000)
        self.mode7.draw(self.screen)
        pygame.draw.rect(self.screen, 0x000000, self.statusArea)
        self.label = self.myFont.render(f"Level {self.level}", True, (255,255,255))
        self.screen.blit(self.label, (400,0))
        self.label = self.myFont.render(f"Score {self.score}", True, (255,255,255))
        self.screen.blit(self.label, (400,30))
        pygame.draw.rect(self.screen, 0x303030, self.progressBarRectBackground)
        
        
        
 
        if self.state == 3:
            
            self.progressBarRect = pygame.rect.Rect(10, self.statusArea.bottom - 10, self.progressBarRectBackground.width * self.FramesSinceStart/self.levelLengthsDict[self.level], 5)
            pygame.draw.rect(self.screen, 0x00ff00, self.progressBarRect)
        elif self.state == 4 and self.FramesSinceStart < 120:
            
            self.progressBarRect = pygame.rect.Rect(10, self.statusArea.bottom - 10, self.progressBarRectBackground.width * self.FramesSinceStart/240, 5)
            pygame.draw.rect(self.screen, 0xff0000, self.progressBarRect)
            
            self.progressBarRect = pygame.rect.Rect(self.statusArea.right - 10 - self.progressBarRectBackground.width * self.FramesSinceStart/240, self.statusArea.bottom - 10, self.progressBarRectBackground.width * self.FramesSinceStart/60, 5)
            pygame.draw.rect(self.screen, 0xff0000, self.progressBarRect)
            
        elif self.state == 4 and self.FramesSinceStart > 120:
            self.progressBarRect = pygame.rect.Rect(10, self.statusArea.bottom - 10, self.progressBarRectBackground.width * bossHp/bossMaxHp, 5)
            pygame.draw.rect(self.screen, 0xff0000, self.progressBarRect)
        
        
        
        
    def renderForeground(self):
        """Useful for showing text above everything else"""
        if self.state == 1:
            self.label = self.myFontBig.render("Super Space Fighter 3 (indev)", True, (255,255,255))
            self.labelRect = self.label.get_rect()
            self.labelRect.center = self.playableArea.center
            self.screen.blit(self.label, self.labelRect.topleft)
            
        
        if self.state == 2:
            self.label = self.myFontBig.render(f"Level {self.level}", True, (255,255,255))
            self.labelRect = self.label.get_rect()
            self.labelRect.center = self.playableArea.center
            self.screen.blit(self.label, self.labelRect.topleft)
            
        if self.state == 4 and self.FramesSinceStart < 120 and self.FramesSinceStart % 16 > 7:
            self.label = self.myFontBig.render("boss incoming", True, (255,0,0))
            self.labelRect = self.label.get_rect()
            self.labelRect.center = self.playableArea.center
            self.screen.blit(self.label, self.labelRect.topleft)
            
        if self.state == 5:
            self.label = self.myFontBig.render("Game Over!", True, (255,0,0))
            self.labelRect = self.label.get_rect()
            self.labelRect.center = self.playableArea.center
            self.screen.blit(self.label, self.labelRect.topleft)
            
        if self.state == 6:
            self.label = self.myFontBig.render(f"Level {self.level} beat!", True, (255,255,255))
            self.labelRect = self.label.get_rect()
            self.labelRect.center = self.playableArea.center
            self.screen.blit(self.label, self.labelRect.topleft)
            
            if self.FramesSinceStart > 90:
            
                self.label = self.myFontBig.render(f"Moving onto level {self.level + 1}", True, (255,255,255))
                self.labelRect = self.label.get_rect()
                self.labelRect.center = self.playableArea.center
                self.labelRect.centery += 30
                self.screen.blit(self.label, self.labelRect.topleft)
            
        
    def finaliseFrame(self):
        self.clock.tick(60)
        pygame.display.flip()
        
        
    
    def closeGame(self):
        pygame.quit()
        print("Game quit successfully")
        
    def returnInputs(self):
        return self.keys
    
    def resetMode7(self, texture1, texture2, fogMode = 0, scale = 100):
        self.mode7 = Mode7(self, texture1, texture2, fogMode, scale)
        self.mode7.speed = 0.01
        
    
    

