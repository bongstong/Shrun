# import all the librarys
import pygame  # to play music
from ursina import Ursina, Entity, Vec2, camera, destroy
from ursina import scene, color, Vec3, BoxCollider, time, raycast, mouse
from ursina import invoke
from time import sleep
from ursina.prefabs.first_person_controller import FirstPersonController
from pygame import mixer  # to play music
import random


# create instance of ursina app
app = Ursina(fullscreen=True)
pygame.init()
mixer.init()

# load music and sounds
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
shot = pygame.mixer.Sound('shot.wav')
shot.set_volume(1)
shotgun_shot = pygame.mixer.Sound('shotgun-sound.wav')
shotgun_shot.set_volume(1)
death_enemy_sound = pygame.mixer.Sound('death.wav')
death_enemy_sound.set_volume(1)
loose_sound = pygame.mixer.Sound('loose.mp3')
loose_sound.set_volume(1)
win_sound = pygame.mixer.Sound('win.mp3')
win_sound.set_volume(1)

# game variables
terrain_width: int = 10
terrain_height: int = 10
score: int = 0
play_win_sounds_death: bool = False
play_win_sounds_vic: bool = False
isGunShotgun: bool = False  # temporary, change if other guns afterwards

# player
controller = FirstPersonController()
controller.collider = BoxCollider(controller, Vec3(0, 1, 0), Vec3(1, 2, 1))


def createEnemy(
    position: tuple = (20, 20, 20), model='billie.stl',
) -> None:

    global enemy
# enemy Entity
    enemy = Entity(
        model=model,
        position=position,
        collider='box',
        health=10,
        scale=(.8, .8, .8)
    )
# rotate the ennemy so he is facing the right direction
    enemy.rotation_y = 180
    enemy.rotation_x = 270
    enemy.rotation_z = 90

    shootables_parent = Entity()
    mouse.traverse_target = shootables_parent

    return None


# create enemies
createEnemy()


# create all little squares for good muzzle flash
def create_muzzle_flash(x, y, z) -> None:
    gun.muzzle_flash = Entity(
        parent=gun,
        z=z,
        y=y,
        x=x,
        world_scale=0.1,
        model='quad',
        color=color.yellow,
        enabled=False,
        rotation_x=90
    )

    return None


shotgunFlash = Entity(
    model='quad',
    parent=camera,
    position=(2, -0.5, .6),
    origin_z=-5,
    enabled=False,
    color=color.orange,
    on_cooldown=False
)


# handgun
gun = Entity(
    model='gun.stl',
    parent=camera,
    position=(.4, -0.5, .6),
    scale=(.032, .032, .032),
    origin_z=-10,
    on_cooldown=False,
    color=color.gray
)

gun.rotation = (-90, 0, 0)
create_muzzle_flash(z=10, y=-11, x=0.5)


def input(key):

    global gun
    global enemy_hp
    global isGunShotgun

    if key == "left mouse down":
        shoot()

        if enemy.health > 0:

            match isGunShotgun:

                case True:
                    hit_info = raycast(
                        camera.world_position, camera.forward, distance=7
                    )
                    if hit_info.hit:
                        enemy.health -= 2

                case False:
                    hit_info = raycast(
                        camera.world_position, camera.forward, distance=15
                    )
                    if hit_info.entity == enemy:
                        enemy.health -= 1

    if key == 'q':
        # destroy previous gun
        destroy(gun)
        isGunShotgun = True

        # shotgun
        gun = Entity(
            model='shotgun.stl',
            parent=camera,
            position=(.6, -3.5, 1),
            scale=(.75, .75, .75),
            origin_z=-4,
            on_cooldown=False,
            color=color.gray,
        )
        gun.rotation = (-90, 0, -15)
        create_muzzle_flash(z=20, y=-20, x=5)

    if key == 'e':
        # destroy previous gun
        destroy(gun)
        isGunShotgun = False

# handgun
        gun = Entity(
            model='gun.stl',
            parent=camera,
            position=(.4, -0.5, .6),
            scale=(.032, .032, .032),
            origin_z=-10,
            on_cooldown=False,
            color=color.gray
        )

        gun.rotation = (-90, 0, 0)
        create_muzzle_flash(z=10, y=-11, x=0.5)


def shoot() -> None:

    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        invoke(gun.muzzle_flash.disable, delay=.05)

        # play right shot sound
        match isGunShotgun:
            case False:
                shot.play()
                invoke(setattr, gun, 'on_cooldown', False, delay=.15)
            case _:
                shotgun_shot.play()
                invoke(setattr, gun, 'on_cooldown', False, delay=1)

        if isGunShotgun is True:
            shotgunFlash.enabled = True
            shotgunFlash.on_cooldown = True
            invoke(shotgunFlash.disable, delay=.4)
            invoke(setattr, shotgunFlash, 'on_cooldown', False, delay=.8)

        return None


def win_sounds() -> None:
    global play_win_sounds_death
    global play_win_sounds_vic

    if play_win_sounds_death is False:
        play_win_sounds_death = True
        death_enemy_sound.play()

    if play_win_sounds_vic is False:
        play_win_sounds_vic = True
        win_sound.play()

    return None


# floor
for index in range(terrain_width**2):
    skibidi_floor = Entity(
        model="plane",
        texture="grass",
        color=color.red,
        collider="box",
        texture_scale=(10, 10),
        scale=(100, 1, 100),
    )


def update():
    # global variables and variables
    global score

    if enemy.health > 0:
        # # Calculate the direction towards the player
        direction = player.position - enemy.position

        speed = 4  # Adjust speed as needed
        enemy.position += direction.normalized() * speed * time.dt
        enemy.position = Vec3(enemy.position.x, 1, enemy.position.z)

        # detect coliison with ennemy
        # from all the sides
        hit_info = raycast(
            camera.world_position, camera.forward, distance=1
        )

        hit_info1 = raycast(
            camera.world_position, camera.back, distance=1
        )

        hit_info2 = raycast(
            camera.world_position, camera.left, distance=1
        )

        hit_info3 = raycast(
            camera.world_position, camera.right, distance=1
        )

        hit_info4 = raycast(
            camera.world_position, camera.down, distance=1
        )

        hit_info5 = raycast(
            camera.world_position, camera.up, distance=1
        )

        # check if I am dead
        if (
            hit_info.entity == enemy or
            hit_info1.entity == enemy or
            hit_info2.entity == enemy or
            hit_info3.entity == enemy or
            hit_info4.entity == enemy or
            hit_info5.entity == enemy
        ):

            # fucking die
            print('score: ', score)
            loose_sound.play()
            sleep(2)
            quit()

            # ************wall/enemy colision detection************************
            # doesn't work yet
        # detect coliison with ennemy/walls
        # from all the sides
        wall_hit_info = raycast(
            enemy.world_position, enemy.forward, distance=5
        )

        # check if enemy touches a wall
        if wall_hit_info.distance != 0.5:
            enemy.position = Vec3(
                enemy.position.x, 1, enemy.position.z
            )

            enemy.position = Vec3(enemy.position.x, 3, enemy.position.z)

        else:
            enemy.position = Vec3(enemy.position.x, 1, enemy.position.z)
            # ************wall/enemy colision detection************************
            # doesn't work yet

    # check if enemy died
    if enemy.health <= 0:

        score += 10
        destroy(enemy)
        win_sounds()


# fog
Entity.default_shader

scene.fog_density = 0.1
scene.fog_color = color.black

# create the labyrinth and walls
locations = set()
for i in range(0, 700):
    x = random.randrange(-50, 50, 2)
    y = 0
    z = random.randrange(-50, 50, 2)
    locations.add((x, y, z))
finish_location = random.choice(list(locations))
locations.remove(finish_location)
finish = Entity(
    model="cube",
    scale=(2, 2, 1),
    color=color.gray.tint(0.4),
    collider="box",
    position=finish_location,
)

for loc in locations:
    cube_width = 2
    cube_height = random.randrange(2, 8, 1)
    cube_depth = 1
    obstacle = Entity(
        model="cube",
        scale=(cube_width, cube_height, cube_depth),
        position=loc,
        texture="brick",
        color=color.gray,
        collider="box",
    )


# create walls
def create_walls(
        scale: tuple = (1, 50, 100), position: tuple = (50, 0, 0)
        ) -> None:

    Entity(
        model="cube",
        scale=scale,
        position=position,
        texture="brick",
        color=color.gray,
        collider="box",
        texture_scale=(50, 50)
    )

    return None


create_walls()
create_walls(
    scale=(1, 50, -100),
    position=(-50, 0, 0)
)
create_walls(
    scale=(100, 50, 1),
    position=(0, 0, 50)
)
create_walls(
    scale=(-100, 50, 1),
    position=(0, 0, -50)
)
# -----*******-------


# create player
player = FirstPersonController(
    mouse_sensitivity=Vec2(80, 80), position=(0, 5, 0)
)


# run the app
app.run()
