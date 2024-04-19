if boss.pos[0] < game.screenX*0.5: # sets the direction of boss' javelin's to point towards centre
                        enemyList.createEnemy(Enemies.Javelin(game.playableArea, 1, initialPos=boss.getCentrePos()))
                    else:
                        enemyList.createEnemy(Enemies.Javelin(game.playableArea, -1, initialPos=boss.getCentrePos()))