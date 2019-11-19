# Imports
import pygame


# Settings
GRID_SIZE = 64
WIDTH = 15 * GRID_SIZE  # 960
HEIGHT = 10 * GRID_SIZE # 640
TITLE = "My Awesome Game"
FPS = 60

WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)


P1_LOC = [3, 4]
P1_IMG = 'images/man_gun.png'
P1_CONTROLS = { 'up': pygame.K_w,
                'down': pygame.K_s,
                'left': pygame.K_a,
                'right': pygame.K_d,
                'shoot': pygame.K_g }

P2_LOC = [10, 7]
P2_IMG = 'images/woman_gun.png'
P2_CONTROLS = { 'up': pygame.K_UP,
                'down': pygame.K_DOWN,
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'shoot': pygame.K_KP0}

PLAYER_SPEED = 5
PLAYER_HEALTH = 5
PLAYER_MAX_HEALTH = 5

WALL_IMG = 'images/block.png'
WALL_LOCS = [[0, 0], [1, 1], [2, 2], [10, 4], [11, 4], [11,5],
             [5, 8], [6, 8], [7, 8]]

GEM_IMG = 'images/gem.png'
GEM_SND = 'sounds/gem.ogg'
GEM_VALUE = 1
GEM_LOCS = [[5, 5], [12, 2], [13, 3], [9, 5]]

BULLET_IMG = 'images/bullet.png'
BULLET_SPEED = 12

TITLE_FONT = None
NORMAL_FONT = None


# Start pygame
pygame.init()
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


# Load assets
''' images '''
p1_rt = pygame.image.load(P1_IMG).convert_alpha()
p1_up = pygame.transform.rotate(p1_rt, 90)
p1_lt = pygame.transform.rotate(p1_rt, 180)
p1_dn = pygame.transform.rotate(p1_rt, 270)
p1_images = [p1_up, p1_rt, p1_dn, p1_lt]
        
p2_rt = pygame.image.load(P2_IMG).convert_alpha()
p2_up = pygame.transform.rotate(p2_rt, 90)
p2_lt = pygame.transform.rotate(p2_rt, 180)
p2_dn = pygame.transform.rotate(p2_rt, 270)
p2_images = [p2_up, p2_rt, p2_dn, p2_lt]

wall_img = pygame.image.load(WALL_IMG).convert_alpha()
gem_img = pygame.image.load(GEM_IMG).convert_alpha()
bullet_img = pygame.image.load(BULLET_IMG).convert_alpha()

''' sounds '''
gem_snd = pygame.mixer.Sound(GEM_SND)


# Sprite classes
class Character(pygame.sprite.Sprite):
    def __init__(self, images, x, y, controls):
        super().__init__()

        self.images = images
        self.direction = 0
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        
        self.rect.centerx = x
        self.rect.centery = y
        self.vx = 0
        self.vy = 0
        
        self.score = 0
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_MAX_HEALTH

        self.controls = controls

    def move(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, walls, False)

        for wall in hits:
            if self.rect.centerx < wall.rect.centerx:
                self.rect.right = wall.rect.left
            else:
                self.rect.left = wall.rect.right

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, walls, False)

        for wall in hits:
            if self.rect.centery < wall.rect.centery:
                self.rect.bottom = wall.rect.top
            else:
                self.rect.top = wall.rect.bottom

    def shoot(self):
        ''' position the bullet at the end of the gun '''
        if self.direction == 0:
            x = self.rect.centerx + 6
            y = self.rect.top - 8
        elif self.direction == 1:
            x = self.rect.right
            y = self.rect.centery + 6
        elif self.direction == 2:
            x = self.rect.centerx - 13
            y = self.rect.bottom
        elif self.direction == 3:
            x = self.rect.left - 8
            y = self.rect.centery - 13

        ''' make sure the player doesn't get hit by it's own bullets when moving '''
        x += self.vx
        y += self.vy
        
        b = Bullet(bullet_img, x, y, self.direction)
        bullets.add(b)
            
        print("Pew!")
        
    def check_edges(self):
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def check_items(self):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)

    def check_bullets(self):
        hits = pygame.sprite.spritecollide(self, bullets, True)

        for bullet in hits:
            self.health -= 1
            print('Oof')

    def die(self):
        self.kill()
        
    def check_status(self):
        if self.health <= 0:
            self.die()
            
    def update_image(self):
        center = self.rect.center
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.center = center

    def process_input(self, keys_pressed, keydown_events):
        self.vx = 0
        self.vy = 0

        if keys_pressed[ self.controls['up'] ]:
            self.vy = -self.speed
            self.direction = 0
        elif keys_pressed[ self.controls['right'] ]:
            self.vx = self.speed
            self.direction = 1
        elif keys_pressed[ self.controls['down'] ]:
            self.vy = self.speed
            self.direction = 2
        elif keys_pressed[ self.controls['left'] ]:
            self.vx = -self.speed
            self.direction = 3

        for event in keydown_events:
            if event.key == self.controls['shoot']:
                self.shoot()
        
    def update(self):
        self.update_image()
        self.move()
        self.check_edges()
        self.check_items()
        self.check_bullets()
        self.check_status()

class Wall(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

class Gem(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def apply(self, character):
        character.score += GEM_VALUE
        gem_snd.play()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, direction):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction

    def move(self):
        if self.direction == 0:
            self.rect.y -= BULLET_SPEED
        elif self.direction == 1:
            self.rect.x += BULLET_SPEED
        elif self.direction == 2:
            self.rect.y += BULLET_SPEED
        elif self.direction == 3:
            self.rect.x -= BULLET_SPEED

    def check_edges(self):
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT or
            self.rect.right < 0 or self.rect.left > WIDTH):
            self.kill()

    def check_walls(self):
        hits = pygame.sprite.spritecollide(self, walls, False)

        if len(hits) > 0:
            self.kill()

    def update(self):
        self.move()
        self.check_walls()
        self.check_edges()


# Debugging functions
def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(window, LIGHT_GRAY, [x, 0], [x, HEIGHT], 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(window, LIGHT_GRAY, [0, y], [WIDTH, y], 1)

def draw_rects():
    all_sprites = pygame.sprite.Group()
    all_sprites.add(players, walls, items, bullets)
    for s in all_sprites:
        pygame.draw.rect(window, LIGHT_GRAY, s.rect, 1)


# Game helper functions        
def draw_text(surface, text, loc, size, color=(0,0,0), family=None, antialias=True, anchor='topleft'):
    text = str(text)
    font = pygame.font.Font(family, size)
    text = font.render(text, antialias, color)
    rect = text.get_rect()

    if   anchor == 'topleft'     : rect.topleft = loc
    elif anchor == 'bottomleft'  : rect.bottomleft = loc
    elif anchor == 'topright'    : rect.topright = loc
    elif anchor == 'bottomright' : rect.bottomright = loc
    elif anchor == 'midtop'      : rect.midtop = loc
    elif anchor == 'midleft'     : rect.midleft = loc
    elif anchor == 'midbottom'   : rect.midtop = loc
    elif anchor == 'midright'    : rect.midleft = loc
    elif anchor == 'center'      : rect.center = loc
    
    surface.blit(text, rect)
        
def display_stats():
    draw_text(window, p1.score, [24, 24], 48, WHITE, anchor='topleft')
    draw_text(window, p2.score, [WIDTH - 24, 24], 48, WHITE, anchor='topright')

def setup():
    global p1, p2, players, walls, items, bullets
    
    players = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    items = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    x1 = P1_LOC[0] * GRID_SIZE + GRID_SIZE // 2
    y1 = P1_LOC[1] * GRID_SIZE + GRID_SIZE // 2
    p1 = Character(p1_images, x1, y1, P1_CONTROLS)

    x2 = P2_LOC[0] * GRID_SIZE + GRID_SIZE // 2
    y2 = P2_LOC[1] * GRID_SIZE + GRID_SIZE // 2
    p2 = Character(p2_images, x2, y2, P2_CONTROLS)
    players.add(p1, p2)

    for loc in WALL_LOCS:
        x = loc[0] * GRID_SIZE + GRID_SIZE // 2
        y = loc[1] * GRID_SIZE + GRID_SIZE // 2
        w = Wall(wall_img, x, y)
        walls.add(w)

    for loc in GEM_LOCS:
        x = loc[0] * GRID_SIZE + GRID_SIZE // 2
        y = loc[1] * GRID_SIZE + GRID_SIZE // 2
        g = Gem(gem_img, x, y)
        items.add(g)


# Game loop
def run():
    grid_on = False
    rect_on = False
    running = True

    while running:
        # Input handling
        keydown_events = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    grid_on = not grid_on
                elif event.key == pygame.K_F2:
                    rect_on = not rect_on
                else:
                    keydown_events.append(event)

        keys_pressed = pygame.key.get_pressed()

        for player in players:
            player.process_input(keys_pressed, keydown_events)
            
        # Game logic
        players.update()
        bullets.update()

        # Drawing code
        window.fill(DARK_GRAY)
        players.draw(window)            
        walls.draw(window)
        items.draw(window)
        bullets.draw(window)
        display_stats()
        
        if rect_on : draw_rects()
        if grid_on : draw_grid()

        # Update display
        pygame.display.update()
        clock.tick(FPS)


# Go!
if __name__ == "__main__":
    setup()
    run()
    pygame.quit()
