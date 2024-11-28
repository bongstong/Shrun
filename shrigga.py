# import all the librarys
from typing import Any
import pygame
import random
from pygame import mixer


pygame.init()
mixer.init()

# setup the screen parameters
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 700
# draw screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ground_scroll = 0
pygame.display.set_caption("Shrigga")

# game variables
GROUND = 650
counter = 0
scroll_speed = 6
in_air = False
last_obstacle = pygame.time.get_ticks()
game_over = False
coin_frequency = random.randint(1000, 3000)  # milliseconds
last_coin = pygame.time.get_ticks()
score = 0
highest_score = []
high_score = 0
MAX_PLATFORMS = 50
platform_frequency = random.randint(2500, 5000)
last_platform = pygame.time.get_ticks()
last_big_platform = pygame.time.get_ticks()
RED = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)  # white
game_paused = False
is_game_active: bool = True


# set fps
clock = pygame.time.Clock()

# load images
ground_img = pygame.image.load("./assets/ground.png")
ground_img = pygame.transform.scale(ground_img, (1687.5, 315))
background = pygame.image.load("./assets/Jungle-Level_background.png")
background = pygame.transform.scale(background, (1687.5, 886.875))

# load menu images
start_img = pygame.image.load("./assets/menu/start_button.png").convert_alpha()
exit_img = pygame.image.load("./assets/menu/exit_button.png").convert_alpha()
background_menu = pygame.image.load("./assets/menu/background.jpeg")
background_menu = pygame.transform.scale(background_menu, (1500, 700))

# load and play music
menu_music = pygame.mixer.Sound("./assets/music.mp3")
menu_channel = pygame.mixer.Channel(1)
game_over_music = pygame.mixer.Sound("./assets/music.mp3")
game_over_channel = pygame.mixer.Channel(2)
pygame.mixer.music.load("./assets/chineeese_song.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)

# load font to display score
score_font = pygame.font.Font("./assets/turok.ttf", 60)


class Ninja(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.ninja_images = []
        self.ninja_index = 0
        self.count = 0
        for num in range(1, 9):
            ninja = pygame.image.load(f"./assets/ninja/ninja{num}.png")
            ninja = pygame.transform.scale(ninja, (88, 96))
            self.ninja_images.append(ninja)
        self.image = self.ninja_images[self.ninja_index]
        self.rect = self.image.get_rect(midbottom=(75, GROUND))
        self.vel = 0
        self.clicked = False

    # setup the player

    def update(self):
        # gravity
        self.vel += 0.21
        if self.vel > 8:
            self.vel = 8
        self.rect.y += int(self.vel)

        if self.rect.bottom >= GROUND:
            self.rect.bottom = GROUND
            self.vel = 0

        # jump
        if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.clicked = True
            self.vel = -10.5
            self.count += 1
            ninja_cooldown = 5

        if pygame.mouse.get_pressed()[0] == 0 and self.rect.bottom == GROUND:
            self.clicked = False

        # check collision with platforms
        for platform in platform_group:
            if platform.rect.colliderect(self.rect):
                if self.rect.bottom < platform.rect.centery:
                    self.rect.bottom = platform.rect.top
                    self.vel = 0

                    # jump from platform
                    if pygame.mouse.get_pressed()[0]:
                        self.clicked = True
                        self.vel = -10.5

        # check collision with double platforms
        for big_platform in big_platform_group:
            if big_platform.rect.colliderect(self.rect):
                if self.rect.bottom < big_platform.rect.centery:
                    self.rect.bottom = big_platform.rect.top
                    self.vel = 0
                    # jump from platform
                    if pygame.mouse.get_pressed()[0] == 1:
                        self.clicked = True
                        self.vel = -10.5

        if self.vel < 0 or self.vel > 1:
            self.ninja_images = []
            self.ninja_index = 0
            self.count = 0
            for num in range(1, 9):
                ninja = pygame.image.load(f"./assets/ninja/ninja{num}.png")
                ninja = pygame.transform.scale(ninja, (88, 96))
                self.ninja_images.append(ninja)
            self.image = self.ninja_images[self.ninja_index]

        # handle the animation
        self.count += 1
        ninja_cooldown = 5
        if self.count > ninja_cooldown:
            self.count = 0
            self.ninja_index += 1
            if self.ninja_index >= len(self.ninja_images):
                self.ninja_index = 0
        self.image = self.ninja_images[self.ninja_index]


# setup obstacles
class obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        c = random.randint(1, 4)
        self.image = pygame.image.load(f"./assets/obstacles/obstacle{c}.png")
        self.image = pygame.transform.scale(self.image, (66.65625, 60.75))
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
        if game_over:
            self.kill()


# setup coins
class coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/coin.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        y_coordinate = random.randint(350, GROUND - 80)
        self.rect.topleft = [x, y_coordinate]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
        if game_over:
            self.kill()


# setup platforms
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        y = 500
        n = int(random.randint(1, 3))
        self.image = pygame.image.load(f"./assets/platforms/platform{n}.png")
        self.image = pygame.transform.scale(self.image, (167.8, 68.6))
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
        if game_over:
            self.kill()


# setup high platforms
class Platform_in_big_air(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        y = 350
        n = int(random.randint(1, 3))
        self.image = pygame.image.load(f"./assets/platforms/platform{n}.png")
        self.image = pygame.transform.scale(self.image, (167.8, 68.6))
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
        if game_over:
            self.kill()


# setup buttons for the menu
class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale))
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


# define groups
obstacle_group = pygame.sprite.Group()
ninja_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
big_platform_group = pygame.sprite.Group()

# player instance
shrek = Ninja(75, GROUND)
ninja_group.add(shrek)
# button instances
start_button = Button(500, 250, start_img, 0.4)
exit_button = Button(700, 250, exit_img, 0.4)
restart_button = Button(500, 250, start_img, 0.4)
game_over_exit_button = Button(700, 250, exit_img, 0.4)

# function to draw score and high score


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# main loop
while is_game_active:
    # draw instances
    screen.blit(background, (0, 0))
    screen.blit(ground_img, (ground_scroll, GROUND))
    ninja_group.draw(screen)
    ninja_group.update()
    shrek.update()
    obstacle_group.draw(screen)
    obstacle_group.update()
    coin_group.draw(screen)
    coin_group.update()
    platform_group.draw(screen)
    platform_group.update()
    big_platform_group.draw(screen)
    big_platform_group.update()

    # draw score
    draw_text("score: " + str(score), score_font, RED, 20, 20)
    draw_text("high score: " + str(high_score), score_font, RED, 20, 60)

    if game_over == False:
        obstacle_frequency = random.randint(1500, 7500)  # milliseconds

        # generate obstacles
        time_now = pygame.time.get_ticks()
        if time_now - last_obstacle > obstacle_frequency:
            stone = obstacle(SCREEN_WIDTH, GROUND - 52)
            obstacle_group.add(stone)
            last_obstacle = time_now

        # Generate coins
        if time_now - last_coin > coin_frequency:
            gold_coin = coin(SCREEN_WIDTH, random.randint(150, GROUND - 150))
            coin_group.add(gold_coin)
            last_coin = time_now

        # Generate platforms
        if time_now - last_platform > platform_frequency:
            air_platform = Platform(SCREEN_WIDTH, random.randint(100, GROUND - 55))
            platform_group.add(air_platform)
            last_platform = time_now

        # generate big air platforms
        if time_now - last_big_platform > platform_frequency:
            big_air_platform = Platform_in_big_air(
                SCREEN_WIDTH + random.randint(155, 465),
                random.randint(100, GROUND - 500),
            )
            big_platform_group.add(big_air_platform)
            last_big_platform = time_now

    # look for collision
    if pygame.sprite.groupcollide(ninja_group, obstacle_group, False, False):
        # reparameter the game settings
        # to stop the game
        game_over = True
        score = 0
        time_now = 0
        old_scroll_speed = scroll_speed
        old_obstacle_frequency = obstacle_frequency
        old_coin_frequency = coin_frequency
        old_platform_frequency = platform_frequency
        scroll_speed = 0
        obstacle_frequency = 9999999
        coin_frequency = 99999999
        platform_frequency = 999999999
        menu_channel.play(menu_music, loops=1)

    # look for collision with coins
    if pygame.sprite.groupcollide(ninja_group, coin_group, False, True):
        score += 1
        highest_score.append(score)
        high_score = max(highest_score)

    ground_scroll -= scroll_speed
    if abs(ground_scroll) > 35:
        ground_scroll = 0

    # change difficulty level
    if score >= 23:
        scroll_speed = 9
        obstacle_frequency = random.randint(800, 2000)
        platform_frequency = random.randint(1500, 4000)
        ground_scroll += 3
    elif score >= 15:
        scroll_speed = 7
        obstacle_frequency = random.randint(1000, 3000)
        platform_frequency = random.randint(2000, 4300)
        ground_scroll += 3
    elif score >= 10:
        scroll_speed = 6
        platform_frequency = random.randint(2200, 4400)
        obstacle_frequency = random.randint(1200, 3500)
        ground_scroll += 2

    # check if the game is paused
    if game_paused == True:
        pygame.mixer.music.stop()
        screen.blit(background_menu, (0, 0))
        start_button.draw(screen)
        exit_button.draw(screen)

        if start_button.clicked:  # Check if the start button is clicked
            game_paused = False
            game_over = False
            scroll_speed = old_scroll_speed
            coin_frequency = old_coin_frequency
            obstacle_frequency = old_obstacle_frequency
            platform_frequency = old_platform_frequency
            menu_channel.stop()
            pygame.mixer.music.play()

        if exit_button.clicked:  # Check if the exit button is clicked
            pygame.quit()

    if game_over == True:
        pygame.mixer.music.stop()
        screen.blit(background_menu, (0, 0))
        restart_button.draw(screen)
        game_over_exit_button.draw(screen)

        if restart_button.clicked:  # Check if the start button is clicked
            score = 0
            game_over = False
            scroll_speed = 6
            coin_frequency = random.randint(1000, 3000)
            obstacle_frequency = random.randint(1500, 7500)
            platform_frequency = random.randint(2500, 5000)
            menu_channel.stop()
            pygame.mixer.music.play()

        if game_over_exit_button.clicked:  # Check if the exit button is clicked
            pygame.quit()

    for event in pygame.event.get():  # event handler
        if event.type == pygame.QUIT:  # quit game loop
            print("Quit")
            is_game_active = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # reparameter the game settings
                # to stop the game
                game_paused = True
                old_scroll_speed = scroll_speed
                old_obstacle_frequency = obstacle_frequency
                old_coin_frequency = coin_frequency
                old_platform_frequency = platform_frequency
                scroll_speed = 0
                obstacle_frequency = 9999999
                coin_frequency = 99999999
                platform_frequency = 999999999
                menu_channel.play(menu_music, loops=1)

    # to display img
    pygame.display.update()  # refresh screen VERY IMPORTANT!!!
    # update_animation()
    clock.tick(60)  # set fps


pygame.quit()
