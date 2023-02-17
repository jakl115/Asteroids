import pygame
from sys import exit
from random import randint


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/starship.png').convert_alpha()
        self.rect = self.image.get_rect(midtop=(screenW / 2, screenH - 100))
        self.speed = 6
        self.blasterXoffset = 14
        self.fireDelay = 250
        self.lastFire = 0

    def player_input(self):
        inputs = pygame.key.get_pressed()  # Input and controls
        if inputs[pygame.K_UP] or inputs[pygame.K_w]:
            self.rect.y -= self.speed;
        if inputs[pygame.K_DOWN] or inputs[pygame.K_s]:
            self.rect.y += self.speed;
        if inputs[pygame.K_LEFT] or inputs[pygame.K_a]:
            self.rect.x -= self.speed;
        if inputs[pygame.K_RIGHT] or inputs[pygame.K_d]:
            self.rect.x += self.speed;
        if inputs[pygame.K_SPACE] or inputs[pygame.K_KP_ENTER]:
            time = pygame.time.get_ticks()
            if time - self.lastFire > self.fireDelay:
                self.lastFire = time
                x = self.rect.centerx
                y = self.rect.centery
                blaster_group.add(Blaster(x - self.blasterXoffset, y))
                blaster_group.add(Blaster(x + self.blasterXoffset, y))

    def bound(self):
        if self.rect.bottom > screenH:  # Player bounding to screen
            self.rect.bottom = screenH
        if self.rect.right > screenW:
            self.rect.right = screenW
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0

    def update(self):
        self.player_input()
        self.bound()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/asteroid.png').convert_alpha()
        sPadding = 16
        self.rect = self.image.get_rect(midbottom=(randint(sPadding, screenW - sPadding), 0))
        self.speed = 1.5

    def bound(self):
        if self.rect.y > screenH + 128:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.bound()

    def rot_center(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Blaster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('images/blaster.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = 7

    def bound(self):
        if self.rect.y < -128:
            self.kill()

    def update(self):
        self.rect.y -= self.speed
        self.bound()


def handle_ui():
    cTime = pygame.time.get_ticks()
    pTime = int((cTime - sTime) / 1000)
    time_surface = font.render(f'{pTime}', False, 'White')
    time_rect = time_surface.get_rect(midtop=(screenW / 2, 0))
    score_surface = font.render(f'{score}', False, 'White')
    score_rect = score_surface.get_rect(topleft=(10, 0))
    screen.blit(score_surface, score_rect)
    screen.blit(time_surface, time_rect)


def collisionP2A():
    if pygame.sprite.spritecollide(player.sprite, asteroid_group, False):
        return 2
    else:
        return 1


def collisionA2B():
    scoreL = 0
    if pygame.sprite.groupcollide(asteroid_group, blaster_group, True, True):
        scoreL += 1
        finalTimer = int(startTimer * (timerMultiplier / (1 + score / scoreSteps)))
        print(finalTimer)
        pygame.time.set_timer(asteroidTimer, finalTimer)
    return scoreL


pygame.init()
pygame.display.set_caption('Asteroids')
screenW = 700
screenH = 900
screen = pygame.display.set_mode((screenW, screenH))
clock = pygame.time.Clock()

sky_surface = pygame.image.load('images/starry.png')  # Sky
skySpeed = 1.5
skyOffset = 0

font = pygame.font.Font('ARCADECLASSIC.TTF', 48)  # UI
minifont = pygame.font.Font('ARCADECLASSIC.TTF', 32)  # UI
gigafont = pygame.font.Font('ARCADECLASSIC.TTF', 96)  # UI
score_surface = font.render('2137', False, 'White')
score_rect = score_surface.get_rect(topleft=(10, 0))
time_surface = font.render('420', False, 'White')
time_rect = time_surface.get_rect(midtop=(screenW / 2, 0))
sTime = 0

player = pygame.sprite.GroupSingle()
player.add(Player())
score = 0
inputs = {}

asteroid_group = pygame.sprite.Group()
blaster_group = pygame.sprite.Group()

asteroidTimer = pygame.USEREVENT + 1  # Asteroid spawn
startTimer = 900
timerMultiplier = 1
scoreSteps = 10
pygame.time.set_timer(asteroidTimer, startTimer)

game_state = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == asteroidTimer and game_state == 1:
            a = Asteroid()
            i = randint(0, 359)
            a.rot_center(i)
            asteroid_group.add(a)

    if game_state == 1:  # Main Game

        skyOffset += skySpeed  # Sky scrolling
        if skyOffset > 225:
            skyOffset = 0
        for i in range(4):
            for x in range(5):
                screen.blit(sky_surface, (0 + (175 * i), -225 + (225 * x + skyOffset)))

        player.update()
        player.draw(screen)
        asteroid_group.update()
        asteroid_group.draw(screen)
        blaster_group.update()
        blaster_group.draw(screen)

        handle_ui()

        game_state = collisionP2A()
        score += collisionA2B()
    if game_state == 2:
        over_surface = gigafont.render('GAME   OVER', False, 'White')
        over_rect = over_surface.get_rect(center=(screenW / 2, screenH / 3))
        rover_surface = minifont.render('press   R   to   retry', False, 'White')
        rover_rect = rover_surface.get_rect(center=(screenW / 2, screenH / 3 + 64))
        mover_surface = minifont.render('press   M   to   return   to   title', False, 'White')
        mover_rect = mover_surface.get_rect(center=(screenW / 2, screenH / 3 + 96))
        qover_surface = minifont.render('press   Q   to   quit', False, 'White')
        qover_rect = qover_surface.get_rect(center=(screenW / 2, screenH / 3 + 128))
        screen.blit(over_surface, over_rect)
        screen.blit(rover_surface, rover_rect)
        screen.blit(mover_surface, mover_rect)
        screen.blit(qover_surface, qover_rect)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_r:
                game_state = 1
                asteroid_group.empty()
                sTime = pygame.time.get_ticks()
                score = 0
                player.empty()
                player.add(Player())
            if event.key == pygame.K_q:
                pygame.quit()
                exit()
            if event.key == pygame.K_m:
                game_state = 0
                asteroid_group.empty()
                score = 0
                player.empty()
    if game_state == 0:
        skyOffset += skySpeed  # Sky scrolling
        if skyOffset > 225:
            skyOffset = 0
        for i in range(4):
            for x in range(5):
                screen.blit(sky_surface, (0 + (175 * i), -225 + (225 * x + skyOffset)))
        title_surface = gigafont.render('ASTEROIDS', False, 'White')
        title_rect = title_surface.get_rect(center=(screenW / 2, screenH / 3))
        play_surface = minifont.render('press   SPACE   to   start', False, 'White')
        play_rect = play_surface.get_rect(center=(screenW / 2, screenH / 3 + 64))
        screen.blit(title_surface, title_rect)
        screen.blit(play_surface, play_rect)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE or event.key == pygame.K_KP_ENTER or event.key == pygame.K_p:
                game_state = 1
                asteroid_group.empty()
                sTime = pygame.time.get_ticks()
                score = 0
                player.empty()
                player.add(Player())

    pygame.display.update()
    clock.tick(120)  # framerate cap AHTUNG PHYSICS BOUND TO FRAMERATE BETHESDA STYLE