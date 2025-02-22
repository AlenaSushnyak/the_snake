from random import choice, randint
from typing import List, Optional, Tuple

import pygame as pg

POINTER = Tuple[int, int]
COLOR = Tuple[int, int, int]

SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR: COLOR = (0, 0, 0)
BORDER_COLOR: COLOR = (93, 216, 228)
APPLE_COLOR: COLOR = (255, 0, 0)
SNAKE_COLOR: COLOR = (0, 255, 0)
DEFAULT_COLOR: COLOR = (2, 2, 2)

INITIAL_SPEED: int = 10
MIN_SPEED: int = 5
MAX_SPEED: int = 20

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock: pg.time.Clock = pg.time.Clock()
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color: COLOR = DEFAULT_COLOR) -> None:
        """
        Инициализирует игровой объект, устанавливая позицию в центре экрана.
        Цвет (body_color) должен быть задан в дочерних классах.
        """
        self.position = SCREEN_CENTER
        self.body_color: COLOR = body_color

    def draw(self):
        """Абстрактный метод отрисовки объекта."""
        raise NotImplementedError('Subclasses should implement this method')


class Apple(GameObject):
    """
    Класс яблока. Яблоко появляется в случайном месте на
    игровом поле и имеет красный цвет.
    """

    def __init__(self, occupied_positions: List[POINTER] = None, body_color: COLOR = APPLE_COLOR) -> None:
        """Инициализирует яблоко: задаёт цвет и случайное положение."""
        super().__init__(body_color=body_color)
        self.occupied_positions = occupied_positions if occupied_positions is not None else []
        self.randomize_position()

    def randomize_position(self) -> None:
        """Устанавливает случайное положение яблока
        в пределах игрового поля.
        """
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in self.occupied_positions:
                self.position = new_position
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на указанной поверхности."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Описывает змейку и её поведение."""

    def __init__(self, body_color: COLOR = SNAKE_COLOR) -> None:
        """Инициализирует змейку с длиной 1, положением в центре экрана,
        направлением вправо и зелёным цветом.
        """
        super().__init__(body_color=body_color)
        self.length: int = 1
        self.positions: List[POINTER] = [self.position]
        self.direction: POINTER = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction: Optional[POINTER] = None
        self.last: Optional[POINTER] = None

    def move(self) -> None:
        """
        Обновляет позицию змейки:
        - Вычисляет новую голову на основе текущего направления.
        - Добавляет новую голову в начало списка позиций.
        - Если длина списка превышает длину змейки, удаляет последний сегмент.
        """
        if self.next_direction:
            self.direction = self.next_direction

        x, y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (x + dx * GRID_SIZE + SCREEN_WIDTH) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE + SCREEN_HEIGHT) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self) -> None:
        """Обновляет направление движения змейки, если задано новое
        направление.move()
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self) -> None:
        """Отрисовывает змейку на указанной поверхности."""
        for positions in self.positions:
            rect = (pg.Rect(positions, (GRID_SIZE, GRID_SIZE)))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> POINTER:
        """Возвращает голову змеи."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None


def handle_keys(snake: Snake, speed: int) -> int:
    """Обрабатывает события клавиатуры для изменения
    направления движения змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN:

            direction_keys = {
                pg.K_UP: UP,
                pg.K_DOWN: DOWN,
                pg.K_LEFT: LEFT,
                pg.K_RIGHT: RIGHT,
            }

            if event.key in direction_keys:
                new_direction = direction_keys[event.key]
                if (new_direction[0] + snake.direction[0], new_direction[
                        1] + snake.direction[1]) != (0, 0):
                    snake.next_direction = new_direction

            if event.key in (pg.K_PLUS, pg.K_EQUALS):
                speed = min(speed + 1, MAX_SPEED)
            elif event.key == pg.K_MINUS:
                speed = max(speed - 1, MIN_SPEED)

    return speed


def draw_info(snake: Snake, speed: int, record_length: int) -> None:
    """Отрисовывает информацию о скорости и рекордной длине."""
    font = pg.font.Font(None, 36)
    if font:
        speed_text = font.render(f'Скорость: {speed}', True, (255, 255, 255))
        record_text = font.render(
            f'Рекорд: {record_length}', True, (255, 255, 255)
        )
        screen.blit(speed_text, (10, 10))
        screen.blit(record_text, (10, 50))


def main() -> None:
    """
    Основной игровой цикл:
      - Создаёт объекты змейки и яблока.
      - Обрабатывает нажатия клавиш, обновляет направление и позицию змейки.
      - Проверяет поедание яблока и столкновение змейки с собой.
      - Отрисовывает объекты и обновляет экран.
    """
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    speed = INITIAL_SPEED
    record_length = 1

    while True:
        clock.tick(speed)
        speed = handle_keys(snake, speed)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

            if snake.length > record_length:
                record_length = snake.length

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position()

        # Отрисовка объектов
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        draw_info(snake, speed, record_length)
        pg.display.update()


if __name__ == '__main__':
    main()
