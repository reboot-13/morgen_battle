from superwires import games, color
import random, math

games.init(screen_width=1000, screen_height=780, fps=100)

class Wrapper (games.Sprite):
    def update(self):
        if self.x < 0:
            self.dx = -self.dx
        if self.x > games.screen.height:
            self.dx = -self.dx

        if self.y > games.screen.width:
            self.dy = -self.dy
        if self.y < 0:
            self.dy = -self.dy

    def die (self):
        self.destroy()

class Collider (games.Sprite):

    def update(self):
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die ()
            self.die ()

    def die (self):
        new_explosion = Explosion(
            x=self.x,
            y=self.y)
        games.screen.add(new_explosion)
        self.destroy()

class Asteroid (Wrapper):
    POINTS = 10   #количество прибавляемых очков
    total = 0     #количество оставшихся астероидов
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    SPAWN = 2  #столько астероидов появляется после разрушения большего или
               # среднего
    images = {
        SMALL: games.load_image('asteroids\\small_main.png'),
        MEDIUM: games.load_image('asteroids\\med_main.png'),
        LARGE: games.load_image('asteroids\\big_main.png')
    }
    SPEED = 2
    def __init__(self, game, x, y, size):
        Asteroid.total += 1
        self.size = size
        self.game = game
        super(Asteroid, self).__init__(
            image = Asteroid.images [size],
            x=x,
            y=y,
            dx = random.choice([1, -1]) * Asteroid.SPEED * random.random() /
                 size,
            dy = random.choice([1, -1]) * Asteroid.SPEED * random.random() /
                 size)

    def die (self):
        Asteroid.total -= 1

        int_score_value = int (self.game.score.value) + (Asteroid.POINTS * self.size)
        self.game.score.value = str (int_score_value)

        self.game.score.right = games.screen.width - 10
        if self.size != Asteroid.SMALL:
            for i in range (Asteroid.SPAWN):
                new_asteroid = Asteroid(game=self.game,
                                        x=self.x,
                                        y=self.y,
                                        size=self.size - 1)
                games.screen.add (new_asteroid)
        super(Asteroid, self).die()
        if Asteroid.total == 0:
            self.game.advance()

class Missle (Collider):
    image = games.load_image('missle\\missle_main.png')
    sound = games.load_sound('sounds and theme\\shot.wav')
    BUFFER = 150
    VELOCITY_FACTOR = 7
    LIFETIME = 130

    def __init__(self, ship_x, ship_y, ship_angle):
        Missle.sound.play()
        angle = ship_angle * math.pi / 180
        buffer_x = Missle.BUFFER * math.sin(angle)
        buffer_y = Missle.BUFFER * -math.cos(angle)
        x = ship_x + buffer_x
        y = ship_y + buffer_y
        dx = Missle.VELOCITY_FACTOR * math.sin(angle)
        dy = Missle.VELOCITY_FACTOR * -math.cos(angle)

        super(Missle, self).__init__(
            image=Missle.image,
            x=x, y=y,
            dx=dx, dy=dy)
        self.lifetime = Missle.LIFETIME

    def update(self):
        super(Missle, self).update()
        
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()


class Ship (Collider):
    image = games.load_image('ship\\spaceship.png')
    ROTATION_STEP = 3
    VELOCITY_STEP = 0.03
    MISSLE_DELAY = 35

    def __init__(self, game, x, y):
        super(Ship, self).__init__(image=Ship.image, x=x, y=x)
        self.missle_wait = 0
        self.game = game

    def update(self):
        super(Ship, self).update()

        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_UP):
            angle = self.angle * math.pi / 180
            self.dx += Ship.VELOCITY_STEP * math.sin (angle)
            self.dy += Ship.VELOCITY_STEP * -math.cos (angle)

        if games.keyboard.is_pressed(games.K_SPACE) and self.missle_wait == 0:
            new_missle = Missle (self.x, self.y, self.angle)
            games.screen.add (new_missle)
            self.missle_wait = Ship.MISSLE_DELAY

        if self.bottom < 0:
            self.top = games.screen.height
        if self.top > games.screen.height:
            self.bottom = 0

        if self.left > games.screen.width:
            self.right = 0
        if self.right < 0:
            self.left = games.screen.width

        if self.missle_wait > 0:
            self.missle_wait -= 1
    def die(self):
        self.game.end ()
        super(Ship, self).die()
        

class Explosion (games.Animation):
    anima_cards = [  # animation of explosion
        '0.gif',
        '1.gif',
        '2.gif',
        '3.gif',
        '4.gif',
        '5.gif',
        '6.gif',
        '7.gif',
        '8.gif',
    ]
    animation_images = []
    for card in anima_cards:
        animation_images.append('explosion\\' + card)

    sound = games.load_sound('sounds and theme\\sound.wav')

    def __init__(self, x, y):
        super(Explosion, self).__init__(images=Explosion.animation_images,
                                        x=x,
                                        y=y,
                                        repeat_interval=4,
                                        n_repeats=1,
                                        is_collideable=False)

class Game:
    def __init__(self):
        self.level = 0
        self.score = games.Text (
            value='0',
            size=60,
            color=color.red,
            top=80,
            right=games.screen.width - 10,
            is_collideable=False)
        games.screen.add (self.score)

        self.ship = Ship(game=self,
            x=games.screen.width / 2,
            y=games.screen.height)
        games.screen.add (self.ship)
        self.play()


    def play(self):
        bg_image = games.load_image('bg\\ok.jpg', transparent=False)
        games.screen.background = bg_image
        games.music.load('sounds and theme\\bg_music.wav')
        games.music.play(-1)
        self.advance ()
        games.screen.mainloop()


    def advance (self):
        self.level += 1
        for i in range (self.level):
            x = random.randrange(games.screen.width)
            y = random.randrange(0, games.screen.height / 3)
            size = random.choice([Asteroid.SMALL, Asteroid.MEDIUM, Asteroid.LARGE])

            the_asteroid = Asteroid(game=self,
                                    x=x, y=y,
                                    size=size)
            games.screen.add(the_asteroid)

        level_message = games.Message (
            value='Уровень' + str (self.level),
            size=80,
            color=color.yellow,
            x=games.screen.width / 2,
            y=games.screen.height / 2,
            lifetime=2 * games.screen.fps,
            is_collideable=False)
        games.screen.add (level_message)

    def end (self):
        end_message = games.Message (
            value='ты проиграл лох',
            size=90,
            color=color.red,
            x=games.screen.width / 2,
            y=games.screen.height / 2,
            lifetime=5 * games.screen.fps,
            is_collideable=False,
            after_death=games.screen.quit)
        games.screen.add (end_message)

def main ():
    the_game = Game()
    the_game.play()

main()