import Game
import PlayerSprite
import Enemies
from random import randint

game = Game.gameClass()
playerBulletList = PlayerSprite.PlayerBulletList()
player = PlayerSprite.Player(game.playableArea, playerBulletList)
powerupList = Enemies.PowerupList()
enemyList = Enemies.EnemyList()
boss = Enemies.Boss(game.playableArea)

# debug
boss.maxHp = boss.hpDict[game.level]
boss.hp = boss.hpDict[game.level]


while game.state != 0:
    
    while game.state == 1: # Title Screen
        #input phase
        game.handleEvents()
        game.handleInputs()
        player.handleInputs()
        
        #update phase
        player.update()
        game.update()

        #render phase
        game.renderBackground()
        player.render(game.screen)
        game.renderForeground()
        game.finaliseFrame() 
        
    while game.state == 2: # Level Start Screen
        #input phase
        game.handleEvents()
        game.handleInputs()
        player.handleInputs()
        
        #update phase
        player.update()
        playerBulletList.update(enemyList, boss, boss.active)
        game.update()

        #render phase
        game.renderBackground()
        player.render(game.screen)
        playerBulletList.render(game.screen)
        game.renderForeground()
        game.finaliseFrame()
        
    while game.state == 3: # Main loop
        #input phase
        game.handleEvents()
        game.handleInputs()
        player.handleInputs()
        
        #update phase
        player.update()
        player.doCollisionDetectionwithEnemies(enemyList)
        game.update()
        enemyList.update(playerBulletList)
        playerBulletList.update(enemyList, boss, boss.active)
        playerBulletList.deleteDeadBullets()
        powerupList.update(playerBulletList, player)
        if powerupList.powerupCollected == 1:
            player.hp += 2
        elif powerupList.powerupCollected == 2:
            player.bulletType = 1
        elif powerupList.powerupCollected == 3:
            player.bulletType = 2
        elif powerupList.powerupCollected == 4:
            player.bulletType = 3
            
        
            
            
        # Spawning patterns        
        if game.level == 1:
            if game.FramesSinceStart % 60 == 59:
                enemyList.createEnemy(Enemies.Bat(game.playableArea, -1, game.pA_RPoRW))   
            if game.FramesSinceStart % 120 == 60 and game.FramesSinceStart > 450:
                enemyList.createEnemy(Enemies.Missile(game.playableArea, player.getCentrePos(), game.pAMidBottom))  
            if game.FramesSinceStart == game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top])) 
                
        elif game.level == 2:
            if game.FramesSinceStart < 600:
                if game.FramesSinceStart % 60 == 59:
                    enemyList.createEnemy(Enemies.Missile(game.playableArea, player.getCentrePos(), list(game.playableArea.midtop)))
                elif game.FramesSinceStart % 60 == 29:
                    enemyList.createEnemy(Enemies.Missile(game.playableArea, player.getCentrePos(), list(game.playableArea.midbottom)))
            else:
                if game.FramesSinceStart % 60 == 59:
                    enemyList.createEnemy(Enemies.Bat(game.playableArea, -1, game.pA_RPoRW)) 
                elif game.FramesSinceStart % 60 == 29:
                    enemyList.createEnemy(Enemies.Bat(game.playableArea, 1, game.pA_RPoLW)) 
            if game.FramesSinceStart == game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top])) 
            if game.FramesSinceStart == game.levelLengthsDict[2] - game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top], powerupType=2)) 
                
        elif game.level == 3:
            if game.FramesSinceStart % 30 == 12:
                enemyList.createEnemy(Enemies.Javelin(game.playableArea, -1 ,game.pA_RPoRW, baseSpeed=10))
            if game.FramesSinceStart == game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top])) 
            if game.FramesSinceStart == 0:
                enemyList.createEnemy(Enemies.Lakitu(game.playableArea, [randint(0,game.playableArea.right),game.playableArea.top + 10]))
            if game.FramesSinceStart == game.levelLengthsDict[3] - game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top], powerupType=3)) 
                
        elif game.level == 4:
            if game.FramesSinceStart < 1000:
                if game.FramesSinceStart % 60 == 59:
                    enemyList.createEnemy(Enemies.FlyBomb(game.playableArea, game.pA_RPoRW))
            else:
                if game.FramesSinceStart % 100 == 99:
                    enemyList.createEnemy(Enemies.FlyBomb(game.playableArea, game.pA_RPoRW, 3))
                if game.FramesSinceStart % 120 == 59:
                    enemyList.createEnemy(Enemies.Missile(game.playableArea, player.getCentrePos(), list(game.playableArea.topright)))
                if game.FramesSinceStart % 120 == 119:
                    enemyList.createEnemy(Enemies.Missile(game.playableArea, player.getCentrePos(), list(game.playableArea.bottomright)))
            if game.FramesSinceStart == game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top])) 
            if game.FramesSinceStart == game.levelLengthsDict[4] - game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top], powerupType=4)) 
                
        elif game.level == 5:
            if game.FramesSinceStart % 90 == 29:
                enemyList.createEnemy(Enemies.SplittingBall(game.playableArea, player.pos, 1, game.pA_RPoRW))
            if game.FramesSinceStart == game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top])) 
            if game.FramesSinceStart == game.levelLengthsDict[5] - game.powerupTimer:
                powerupList.createEnemy(Enemies.PowerUp(game.playableArea, [randint(0,game.playableArea.width), game.playableArea.top], powerupType=randint(2,4))) 
                    
            
                    
        if player.returnDeathState():
            game.state = 5
            
        # triggers
        for i in range(len(enemyList.triggerList)):
            if enemyList.triggerList[i][0] == "FlyBomb Explosion":
                for _ in range(8):
                    enemyList.createEnemy(Enemies.Fly(game.playableArea, enemyList.triggerList[i][1], baseSpeed=4))

            elif enemyList.triggerList[i][0] == "Lakitu Drop Stone":
                enemyList.createEnemy(Enemies.Stone(game.playableArea, enemyList.triggerList[i][1]))
                
            elif enemyList.triggerList[i][0] == "SplittingBall Split":
                for _ in range(2):
                    enemyList.createEnemy(Enemies.SplittingBall(game.playableArea, player.pos, enemyList.triggerList[i][2], [enemyList.triggerList[i][1][0]+randint(-30,30),enemyList.triggerList[i][1][1]+randint(-30,30)]))
                    
        
        #render phase
        game.renderBackground()
        player.render(game.screen)
        playerBulletList.render(game.screen)
        powerupList.render(game.screen)
        enemyList.render(game.screen)
        boss.renderStats(game.screen)
        game.renderForeground()
        
        
        game.finaliseFrame()
        
    while game.state == 4: # Boss
        
            
        #input phase
        game.handleEvents()
        game.handleInputs()
        player.handleInputs()
        
        #update phase
        player.update()      
        enemyList.update(playerBulletList)
        game.update()
        player.doCollisionDetectionwithEnemies(enemyList)
            
        if boss.invulnerable == False:
            boss.doCollisionDetectionwithBullets(playerBulletList)
        playerBulletList.update(enemyList, boss, boss.active)
        
        if game.FramesSinceStart == 0: #syncs frame clocks
            boss.FramesSinceStart = 0
        
        if game.FramesSinceStart == 120:
            boss.active = True
            boss.visible = True
            enemyList.killAll()
            
        
        
        
        
        boss.update(player.getCentrePos(), game.level)
        playerBulletList.deleteDeadBullets()
        
        # Spawning patterns
        if boss.active:
            player.doCollisionDetectionwithBoss(boss)
            
        
            if game.level == 1:
                if boss.FramesSinceStart % 90 == 45:
                    enemyList.createEnemy(Enemies.Missile(game.playableArea, player.getCentrePos(), boss.getCentrePos()))
                    
            elif game.level == 2:
                if boss.FramesSinceStart % 45 == 40:
                    if boss.pos[0] < game.screenX*0.5: # sets the direction of boss' javelin's to point towards centre
                        enemyList.createEnemy(Enemies.Javelin(game.playableArea, 1, initialPos=boss.getCentrePos()))
                    else:
                        enemyList.createEnemy(Enemies.Javelin(game.playableArea, -1, initialPos=boss.getCentrePos()))
                        
            elif game.level == 3:
                if boss.FramesSinceStart % 45 == 40 and boss.bossPhase == 0:
                    enemyList.createEnemy(Enemies.Missile(game.playableArea, player.getCentrePos(), boss.getCentrePos(), 16))
                    
            elif game.level == 4:
                if boss.FramesSinceStart % 31 == 14:
                    if boss.bossPhase == 0:
                        enemyList.createEnemy(Enemies.FlyProjectile(game.playableArea, [boss.pos[0]+16,boss.pos[1]+32], [0,10]))
                        if game.FramesSinceStart % 2 == 1:
                            enemyList.createEnemy(Enemies.FlyProjectile(game.playableArea, boss.getCentrePos(), [-10,0]))
                        else:
                            enemyList.createEnemy(Enemies.FlyProjectile(game.playableArea, boss.getCentrePos(), [10,0]))
                if game.FramesSinceStart % 180 == 119:
                    if randint(0,1) == 1:
                        enemyList.createEnemy(Enemies.FlyBomb(game.playableArea,game.pA_RPoLW, 4, 1))
                    else:
                        enemyList.createEnemy(Enemies.FlyBomb(game.playableArea,game.pA_RPoRW, 4, -1))
        
        # triggers
        for i in range(len(enemyList.triggerList)):
            if enemyList.triggerList[i][0] == "FlyBomb Explosion":
                for _ in range(8):
                    enemyList.createEnemy(Enemies.Fly(game.playableArea, enemyList.triggerList[i][1], baseSpeed=4))

            elif enemyList.triggerList[i][0] == "Lakitu Drop Stone":
                enemyList.createEnemy(Enemies.Stone(game.playableArea, enemyList.triggerList[i][1]))
                
            elif enemyList.triggerList[i][0] == "SplittingBall Split":
                for _ in range(2):
                    enemyList.createEnemy(Enemies.SplittingBall(game.playableArea, player.pos, enemyList.triggerList[i][2], [enemyList.triggerList[i][1][0]+randint(-30,30),enemyList.triggerList[i][1][1]+randint(-30,30)]))
        
                    
                    
        if boss.returnDeathState():
            game.state = 6
            boss.active = False
            boss.visible = False
            game.score += 1000
            if player.hp < 8:
                player.hp += 1

        if player.returnDeathState():
            game.state = 5
            
        
            
            
        #render phase
        game.renderBackground(boss.hp, boss.maxHp)
        player.render(game.screen)
        playerBulletList.render(game.screen)
        enemyList.render(game.screen)
        boss.render(game.screen)
        boss.renderStats(game.screen)
        game.renderForeground()
        
        game.finaliseFrame()
            
    while game.state == 5: # game over screen
        #input phase
        game.handleEvents()
        game.handleInputs()
        
        #update phase
        game.update()
        if game.FramesSinceStart == 6:
            game.gameoverSound.play()

        #render phase
        game.renderBackground()
        game.renderForeground()
        game.finaliseFrame() 
        
    while game.state == 6: # level win screen
        #input phase
        game.handleEvents()
        game.handleInputs()
        player.handleInputs()
        
        #update phase
        game.update()
        player.update()
        enemyList.update(playerBulletList)
        playerBulletList.update(enemyList, boss, boss.active)
        playerBulletList.deleteDeadBullets()
        if game.FramesSinceStart == 0:
            boss.maxHp = boss.hpDict[game.level + 1]
            boss.hp = boss.maxHp
            enemyList.killAll()

        #render phase
        game.renderBackground()
        player.render(game.screen)
        playerBulletList.render(game.screen)
        game.renderForeground()
        game.finaliseFrame() 
        # level incriments as this state endsa
         
        
    
    
game.closeGame()