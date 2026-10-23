import random
import pygame

from game.player import Player
from game.coin import Coin
from game.collection import check_collection
from game.renderer import WIDTH, HEIGHT


NUM_COINS = 10
NUM_OBSTACLES = 5
OBSTACLE_SIZE = 40
STARTING_LIVES = 3
GAME_DURATION = 30

COIN_TYPES = [
    {"value": 1, "color": (205, 127, 50)},   # Bronze
    {"value": 3, "color": (192, 192, 192)},  # Silver
    {"value": 5, "color": (255, 215, 0)},    # Gold
]


class GameEngine:

    def __init__(self):
        self.player = Player(100, 100)
        self.coins = [self._random_coin() for _ in range(NUM_COINS)]
        self.score = 0

        self.lives = STARTING_LIVES
        self.obstacles = self._create_obstacles()
        self.obstacle_hit = False

        self.time_left = GAME_DURATION
        self.start_time = pygame.time.get_ticks()
        self.game_over = False

    def _random_coin(self):
        x = random.randint(30, WIDTH - 30)
        y = random.randint(30, HEIGHT - 30)

        coin_type = random.choice(COIN_TYPES)

        return Coin(
            x=x,
            y=y,
            radius=12,
            value=coin_type["value"],
            color=coin_type["color"],
        )

    def _create_obstacles(self):
        obstacles = []

        for _ in range(NUM_OBSTACLES):
            x = random.randint(
                OBSTACLE_SIZE,
                WIDTH - OBSTACLE_SIZE
            )
            y = random.randint(
                OBSTACLE_SIZE,
                HEIGHT - OBSTACLE_SIZE
            )

            rect = pygame.Rect(
                x - OBSTACLE_SIZE // 2,
                y - OBSTACLE_SIZE // 2,
                OBSTACLE_SIZE,
                OBSTACLE_SIZE,
            )

            obstacles.append(rect)

        return obstacles

    def handle_input(self, keys_pressed):
        if self.game_over:
            if keys_pressed[pygame.K_r]:
                self.restart()
            return

        dx = dy = 0

        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed

        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed

        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed

        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed

        self.player.move(dx, dy, WIDTH, HEIGHT)

    def update(self):
        if self.game_over:
            return

        # Coin collection
        collected = check_collection(
            self.player,
            self.coins
        )

        for coin in collected:
            self.score += coin.value
            self.coins.remove(coin)

        # Obstacle collision
        player_rect = self.player.get_rect()

        touching_obstacle = any(
            player_rect.colliderect(obstacle)
            for obstacle in self.obstacles
        )

        if touching_obstacle and not self.obstacle_hit:
            self.lives -= 1
            self.obstacle_hit = True

        if not touching_obstacle:
            self.obstacle_hit = False

        # Timer
        elapsed_seconds = (
            pygame.time.get_ticks() - self.start_time
        ) // 1000

        self.time_left = max(
            0,
            GAME_DURATION - elapsed_seconds
        )

        # Game over
        if self.time_left <= 0 or self.lives <= 0:
            self.game_over = True

    def restart(self):
        self.player = Player(100, 100)
        self.coins = [
            self._random_coin()
            for _ in range(NUM_COINS)
        ]

        self.score = 0
        self.lives = STARTING_LIVES
        self.obstacles = self._create_obstacles()
        self.obstacle_hit = False

        self.time_left = GAME_DURATION
        self.start_time = pygame.time.get_ticks()
        self.game_over = False

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_scene(
            surface,
            self.player,
            self.coins,
            self.obstacles
        )

        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}",
            (10, 10)
        )

        renderer.draw_text(
            surface,
            font,
            f"Lives: {self.lives}",
            (10, 40)
        )

        renderer.draw_text(
            surface,
            font,
            f"Time: {self.time_left}",
            (10, 70)
        )

        if self.game_over:
            renderer.draw_banner(
                surface,
                font,
                f"GAME OVER - Score: {self.score} - Press R to Restart"
            )