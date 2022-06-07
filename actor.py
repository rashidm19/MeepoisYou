import pygame
from typing import Tuple, Optional
from settings import *

class Actor:
    """
    A class that represents all the actors in the game. This class includes any
    attributes/methods that are common between the actors

    === Public Attributes ===
    x:
        x coordinate of this actor's location on the stage
    y:
        y coordinate of this actor's location on the stage
    image:
        the image of the actor

    === Private Attributes ===
    _is_stop:
        Flag to keep track of whether this object cannot be moved through
    _is_push:
        Flag to keep track of whether this object is pushable

    Representation Invariant: x,y must be greater or equal to 0
    """
    x: int
    y: int
    _is_stop: bool
    _is_push: bool
    image: pygame.Surface

    def __init__(self, x: int, y: int) -> None:

        self.x, self.y = x, y
        self._is_stop = False
        self._is_push = False
        self.image = pygame.Surface((TILESIZE, TILESIZE))

    def is_stop(self) -> bool:
        """
        Getter for _is_stop
        """
        return self._is_stop

    def is_push(self) -> bool:
        """
        Getter for _is_push
        """
        return self._is_push

    def copy(self) -> 'Actor':
        """
        Creates an identical copy of self and returns the new copy
        To be implemented in the subclasses
        """
        raise NotImplementedError

    def move(self, game_: 'Game', dx: int, dy: int) -> bool:
        """
        Function to move an Actor on the screen, to the direction
        indicated by dx and dy

        game_: the Game object
        dx: the offset in the x coordinate
        dx: the offset in the y coordinate

        Returns whether <self> actually moves.
        """
        rside = game_.get_actor(self.x+1, self.y)
        lside = game_.get_actor(self.x-1, self.y)
        up = game_.get_actor(self.x, self.y-1)
        down = game_.get_actor(self.x, self.y+1)
        if rside:
            if rside.is_push():
                if dx > 0:
                    # rside = game_.get_actor(self.x+1, self.y)
                    rside.move(game_, dx, dy)

                    rside_bush = game_.get_actor(self.x +dx, self.y)
                    if rside_bush and rside_bush.is_stop:
                        return False

            elif rside.is_stop():
                if dx > 0:
                    return False

        if lside:
            if lside.is_push():
                if dx < 0:
                    # lside = game_.get_actor(self.x -1, self.y)
                    lside.move(game_, dx, dy)

                    lside_bush = game_.get_actor(self.x +dx, self.y)
                    if lside_bush and lside_bush.is_stop:
                        return False
            elif lside.is_stop():
                if dx < 0:
                    return False
        if up:
            if up.is_push():
                if dy < 0:
                    # up = game_.get_actor(self.x, self.y-1)
                    up.move(game_, dx, dy)

                    up_bush = game_.get_actor(self.x, self.y + dy)
                    if up_bush and up_bush.is_stop:
                        return False
            elif up.is_stop():
                if dy < 0:
                    return False
        # if down:
        #     if down.is_push() and not down.is_stop():
        #         if dy > 0:
        #             # down = game_.get_actor(self.x, self.y+1)
        #             down.move(game_, dx, dy)
        #
        #             down_bush = game_.get_actor(self.x, self.y + dy)
        #             if down_bush and down_bush.is_stop:
        #                 return False
        #     else:
        #         if dy > 0:
        #             return False
        if down:
            if down.is_push():
                if dy > 0:
                    # down = game_.get_actor(self.x, self.y+1)
                    down.move(game_, dx, dy)

                    down_bush = game_.get_actor(self.x, self.y + dy)
                    if down_bush and down_bush.is_stop:
                        return False
            elif down.is_stop():
                if dy > 0:
                    return False

        self.y += dy
        self.x += dx
        x1 = game_.x_tiles
        y1 = game_.y_tiles
        if self.x <= 0:
            self.x = 0
        elif self.x >= x1:
            self.x = x1
        if self.y <= 0:
            self.y = 0
        elif self.y >= y1:
            self.y = y1
        return True


class Character(Actor):
    """
    A class that represents non-Blocks/Bushes on the screen
    i.e., Meepo, Wall, Rock, Flag

    A Character could potentially be the player that is controlled by the
    key presses

    === Additional Private Attributes ===
    _is_player:
        Whether the character is the player, i.e., "<Character> isYou"
    _is_lose:
        Whether the rules contains "<Character> isLose"
    _is_win:
        Whether the rules contains "<Character> isWin"
    """
    _is_player: bool
    _is_lose: bool
    _is_win: bool

    def __init__(self, x: int, y: int) -> None:
        """
        Initializes the Character
        """
        super().__init__(x, y)
        self._is_player = False
        self._is_lose = False
        self._is_win = False

    def is_win(self) -> bool:
        """
        Getter for _is_win
        """
        return self._is_win

    def is_lose(self) -> bool:
        """
        Getter for _is_lose
        """
        return self._is_lose

    def is_player(self) -> bool:
        """
        Getter for _is_player
        """
        return self._is_player

    def set_player(self) -> None:
        """
        Sets flag to make this actor the player.
        """
        self._is_player = True
        self._is_stop = False
        self._is_push = False

    def unset_player(self) -> None:
        """
        Unsets the flag to make the actor not the player.
        """
        self._is_player = False

    def set_stop(self) -> None:
        """
        Sets flag to make actor incapable of being moved through or pushed.
        """
        self._is_stop = True
        # self._is_push = False
        # self._is_player = False

    def unset_stop(self) -> None:
        """
        Unsets the flag that prevents actor from being moved through or pushed.
        """
        self._is_stop = False

    def set_push(self) -> None:
        """
        Sets the flag that allows the actor to be pushable
        """
        self._is_push = True
        # self._is_stop = False
        # self._is_player = False

    def unset_push(self) -> None:
        """
        Unsets the flag that allows the actor to be pushable
        """
        self._is_push = False

    def set_win(self) -> None:
        """
        Sets this actor to be the win Condition.
        """
        self._is_win = True
        self._is_lose = False

    def unset_win(self) -> None:
        """
        Unsets this actor from being the win Condition.
        """
        self._is_win = False

    def set_lose(self) -> None:
        """
        Sets this flag to be the lose condition.
        """
        self._is_lose = True
        self._is_win = False

    def unset_lose(self) -> None:
        """
        Unsets this flag from being the lose condition.
        """
        self._is_lose = False

    def copy_flags(self, other: "Character") -> None:
        """
        Copy the boolean flags to the <other> object
        This is a helper method that should be used by the copy methods
        implemented in the subclasses.
        """
        other._is_player = self._is_player
        other._is_push = self._is_push
        other._is_stop = self._is_stop
        other._is_lose = self._is_lose
        other._is_win = self._is_win

    def copy(self) -> 'Character':
        """
        Returns a copy of this object itself.
        Need to be implemented in the subclasses
        """
        raise NotImplementedError

    def handle_key_press(self, game_: 'Game') -> Tuple[int, int]:
        """
        Process the key press input and
        return (dx, dy), the offsets on the x and y directions.
        """
        key_pressed = game_.keys_pressed
        dx, dy = 0, 0
        if key_pressed[pygame.K_LEFT]:
            dx -= 1
        elif key_pressed[pygame.K_RIGHT]:
            dx += 1
        elif key_pressed[pygame.K_UP]:
            dy -= 1
        elif key_pressed[pygame.K_DOWN]:
            dy += 1
        return dx, dy

    def player_move(self, game_: 'Game') -> bool:
        """
        Detects input from the keyboard and moves the Player on the game stage
        based on directional key presses.

        Also, after the move, check if we have won or lost the game,
        and call the win() and lose() methods in Game accordingly
        """
        dx, dy = self.handle_key_press(game_)
        if dx == 0 and dy == 0:
            return False
        return self.move(game_, dx, dy)


class Meepo(Character):
    """
    Class representing Ms. Meepo in the game.

    Meepo is a special Character because we want to change her image as
    she moves in different directions. We also want to see the movement of
    her "arms" as she moves.

    === Additional Public Attributes ===
    walk_right:
        Image for walking right
    walk_left:
        Image for walking left
    walk_up:
        Image for walking up
    walk_down:
        Image for walking down
    """
    walk_left: list
    walk_right: list
    walk_down: list
    walk_up: list

    def __init__(self, x: int, y: int) -> None:
        """
        Initializes the Meepo Class
        Load the images for displaying Ms. Meepo's movement.
        """
        super().__init__(x, y)

        # Add motion images
        self.walk_right = [load_image(PLAYER_SPRITE_R1),
                           load_image(PLAYER_SPRITE_R2)]
        self.walk_left = [
            pygame.transform.flip(load_image(PLAYER_SPRITE_R1), True, False),
            pygame.transform.flip(load_image(PLAYER_SPRITE_R2), True, False)
        ]
        self.walk_up = [load_image(PLAYER_SPRITE_U1),
                        load_image(PLAYER_SPRITE_U2)]
        self.walk_down = [load_image(PLAYER_SPRITE_B1),
                          load_image(PLAYER_SPRITE_B2)]
        self.image = self.walk_down[1]

    def copy(self):
        '''
        Returns a copy of this object itself.
        '''
        mcopy = Meepo(self.x, self.y)
        self.copy_flags(mcopy)
        return mcopy


    def handle_key_press(self, game_: 'Game') -> Tuple[int, int]:
        """
        Overriding the same method in the base class, adding the modification
        of the image depending on the direction of the move.
        """
        key_pressed = game_.keys_pressed
        dx, dy = 0, 0
        if key_pressed[pygame.K_LEFT]:
            if self.image == self.walk_left[0]:
                self.image = self.walk_left[1]
            elif self.image != self.walk_left[1]:
                self.image = self.walk_left[0]
            elif self.image == self.walk_left[1]:
                self.image = self.walk_left[0]
            dx -= 1

        elif key_pressed[pygame.K_RIGHT]:
            if self.image == self.walk_right[1]:
                self.image = self.walk_right[0]
            elif self.image != self.walk_right[0]:
                self.image = self.walk_right[1]
            elif self.image == self.walk_right[0]:
                self.image = self.walk_right[1]
            dx += 1
        elif key_pressed[pygame.K_UP]:
            if self.image == self.walk_up[0]:
                self.image = self.walk_up[1]
            elif self.image != self.walk_up[1]:
                self.image = self.walk_up[0]
            elif self.image == self.walk_up[1]:
                self.image = self.walk_up[0]
            dy -= 1
        elif key_pressed[pygame.K_DOWN]:
            if self.image == self.walk_down[1]:
                self.image = self.walk_down[0]
            elif self.image != self.walk_down[0]:
                self.image = self.walk_down[1]
            elif self.image == self.walk_down[0]:
                self.image = self.walk_down[1]
            dy += 1
        return (dx,dy)

class Wall(Character):

    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y)
        self.image = load_image(WALL_SPRITE)

        # Bush is always unmovable and cannot be moved through
        # Wall can be pushed
        self._is_stop = False
        self._is_push = False

    def copy(self) -> 'Wall':
        """
        Returns a copy of the Wall object
        """
        wcopy = Wall(self.x, self.y)
        self.copy_flags(wcopy)

        return wcopy


class Rock(Character):

    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y)
        self.image = load_image(ROCK_SPRITE)

        # Bush is always unmovable and cannot be moved through
        # Rock can be moved
        self._is_stop = True
        self._is_push = False

    def copy(self) -> 'Rock':
        """
        Returns a copy of the Bush object
        """
        rcopy = Rock(self.x, self.y)
        self.copy_flags(rcopy)

        return rcopy


class Flag(Character):

    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y)
        self.image = load_image(FLAG_SPRITE)

        self._is_stop = False
        self._is_push = False

    def copy(self) -> 'Flag':
        """
        Returns a copy of the Bush object
        """
        fcopy = Flag(self.x, self.y)
        self.copy_flags(fcopy)
        return fcopy


class Bush(Actor):
    """
    Class representing the edges and unmovable objects in the game.
    """
    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y)
        self.image = load_image(BUSH_SPRITE)

        # Bush is always unmovable and cannot be moved through
        self._is_stop = True
        self._is_push = False

    def copy(self) -> 'Bush':
        """
        Returns a copy of the Bush object
        """

        return Bush(self.x, self.y)


class Block(Actor):
    """
    Class for words in the game such as
    "Meepo", "you", "is", "rock", "lose", "victor", "flag", "push", and "stop".

    Blocks are used for indicating rules in the game.

    ================
    Additional public attribute:
    word: the word on this block
    """
    word: str

    def __init__(self, x: int, y: int, word_: str) -> None:

        super().__init__(x, y)
        self.word = word_
        # Blocks are always pushable and cannot be moved through.
        self._is_push = True
        self._is_stop = False

    def copy(self) -> 'Block':
        """
        Creates an identical copy of self and returns the new copy.
        To be implemented in the subclasses
        """
        raise NotImplementedError


class Subject(Block):
    """
    Class representing the Subject blocks in the game, e.g.,
    "Meepo", "Wall", "Flag", "Rock" (see SUBJECTS in settings.py)
    """
    def __init__(self, x, y, word_):
        super().__init__(x,y,word_)

        self.image = load_image(WORDS_SPRITES[word_.lower()])

    def copy(self):
        '''
        Creates an identical copy of self and returns the new copy.
        '''

        return Subject(self.x, self.y, self.word)




class Attribute(Block):
    """
    Class representing the Attribute blocks in the game, e.g.,
    "Push", "Stop", "Victory", "Lose", "You"
    """
    def __init__(self, x, y, word_):
        super().__init__(x,y,word_)
        self.image = load_image(WORDS_SPRITES[word_.lower()])

    def copy(self):
        '''
        Creates an identical copy of self and returns the new copy.
        '''

        return Attribute(self.x, self.y, self.word)

class Is(Block):
    """
    Class representing the Is blocks in the game.
    """

    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y, " is")  # Note the space in " is"
        self.image = load_image(IS_PURPLE)

    def copy(self):
        '''
        Creates an identical copy of self and returns the new copy.
        '''
        block_is = Is(self.x, self.y)
        block_is.image = self.image
        return block_is

    def update(self, up: Optional[Actor],
               down: Optional[Actor],
               left: Optional[Actor],
               right: Optional[Actor]) -> Tuple[str, str]:
        """
        Detect horizontally and vertically if a new rule has been created in
        the format of a string "Subject isAttribute".

        up, down, left, right: the Actors that are adjacent (in the four
        directions) to this IS block

        Return a tuple of (horizontal, vertical) rules if a rule is detected
        in either direction, otherwise put an empty string at the tuple index.
        """
        # TODO Task 3: Complete this method.
        vert = ''
        horiz = ''
        flag = 0
        if left and right and type(left) != Bush and type(right)!= Bush:
            try:
                if left.word in list(SUBJECTS.values()) and right.word in list(ATTRIBUTES.values()):
                    flag = 1
                    self.image = load_image(IS_LIGHT_BLUE)
                    horiz = left.word + ' is' + right.word
            except AttributeError:
                self.image = load_image(IS_PURPLE)

        else:
            self.image = load_image(IS_PURPLE)

        if up and down and type(up) != Bush and type(down) != Bush:
            # print(type(up), up)
            # print(Bush)
            try:
                if up.word in list(SUBJECTS.values()) and down.word in list(ATTRIBUTES.values()):
                    if flag == 1:
                        self.image = load_image(IS_DARK_BLUE)
                    else:
                        self.image = load_image(IS_LIGHT_BLUE)
                    vert = up.word + ' is' + down.word
            except AttributeError:
                self.image = load_image(IS_PURPLE)

        else:
            if flag == 0:
                self.image = load_image(IS_PURPLE)
        return horiz, vert


def load_image(img_name: str, width: int = TILESIZE,
               height: int = TILESIZE) -> pygame.image:
    """
    Return a pygame img of the PNG img_name that has been scaled according
    to the given width and size
    """
    img = pygame.image.load(img_name).convert_alpha()
    return pygame.transform.scale(img, (width, height))


if __name__ == "__main__":

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['settings', 'stack', 'actor', 'pygame']
    })
