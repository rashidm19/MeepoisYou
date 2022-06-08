from typing import Any, Type, Tuple, List, Sequence, Optional
import pygame
from settings import *
from stack import Stack
import actor


class Game:
    """
    Class representing the game.
    
    In order to run the game, this file has to be compiled.
    """
    size: Tuple[int, int]
    width: int
    height: int
    screen: Optional[pygame.Surface]
    x_tiles: int
    y_tiles: int
    tiles_number: Tuple[int, int]
    background: Optional[pygame.Surface]

    _actors: List[actor.Actor]
    _is: List[actor.Is]
    _running: bool
    _rules: List[str]
    _history: Stack

    player: Optional[actor.Actor]
    map_data: List[str]
    keys_pressed: Optional[Sequence[bool]]

    def __init__(self) -> None:
        """
        Initialize variables for this Class.
        """
        self.width, self.height = 0, 0
        self.size = (self.width, self.height)
        self.screen = None
        self.x_tiles, self.y_tiles = (0, 0)
        self.tiles_number = (self.x_tiles, self.y_tiles)
        self.background = None

        # TODO Task 1: complete the initializer of the Game class
        self._actors = []
        self._is = []
        self._running = True
        self._rules = []
        self._history = Stack()

        self.player = None
        self.map_data = []
        self.keys_pressed = None

    def load_map(self, path: str) -> None:
        """
        Reads a .txt file representing the map
        """
        with open(path, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.width = (len(self.map_data[0])) * TILESIZE
        self.height = len(self.map_data) * TILESIZE
        self.size = (self.width, self.height)
        self.x_tiles, self.y_tiles = len(self.map_data[0]), len(self.map_data)

        # center the window on the screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def new(self) -> None:
        """
        Initialize variables to be object on screen.
        """
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(
            "{}/backgroundBig.png".format(SPRITES_DIR)).convert_alpha()
        for col, tiles in enumerate(self.map_data):
            for row, tile in enumerate(tiles):
                if tile.isnumeric():
                    self._actors.append(
                        Game.get_character(CHARACTERS[tile])(row, col))
                elif tile in SUBJECTS:
                    self._actors.append(
                        actor.Subject(row, col, SUBJECTS[tile]))
                elif tile in ATTRIBUTES:
                    self._actors.append(
                        actor.Attribute(row, col, ATTRIBUTES[tile]))
                elif tile == 'I':
                    is_tile = actor.Is(row, col)
                    self._is.append(is_tile)
                    self._actors.append(is_tile)

    def get_actors(self) -> List[actor.Actor]:
        """
        Getter for the list of actors
        """
        return self._actors

    def get_running(self) -> bool:
        """
        Getter for _running
        """
        return self._running

    def get_rules(self) -> List[str]:
        """
        Getter for _rules
        """
        return self._rules

    def _draw(self) -> None:
        """
        Draws the screen, grid, and objects/players on the screen
        """
        self.screen.blit(self.background,
                         (((0.5 * self.width) - (0.5 * 1920),
                           (0.5 * self.height) - (0.5 * 1080))))
        for actor_ in self._actors:
            rect = pygame.Rect(actor_.x * TILESIZE,
                               actor_.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(actor_.image, rect)

        # Blit the player at the end to make it above all other objects
        if self.player:
            rect = pygame.Rect(self.player.x * TILESIZE,
                               self.player.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(self.player.image, rect)

        pygame.display.flip()

    def _events(self) -> None:
        """
        Event handling of the game window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            # Allows us to make each press count as 1 movement.
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed = pygame.key.get_pressed()
                ctrl_held = self.keys_pressed[pygame.K_LCTRL]

                # handle undo button and player movement here
                if event.key == pygame.K_z and ctrl_held:   # Ctrl-Z
                    self._undo()
                else:
                    if self.player is not None:
                        assert isinstance(self.player, actor.Character)
                        save = self._copy()
                        # we create a copy of Game class
                        # print(save)
                        if self.player.player_move(self) and not self.win_or_lose():
                            #
                            self._history.push(save)
        return

    def win_or_lose(self) -> bool:
        """
        Check if the game has won or lost
        Returns True if the game is won or lost; otherwise return False
        """
        assert isinstance(self.player, actor.Character)
        for ac in self._actors:
            if isinstance(ac, actor.Character) \
                    and ac.x == self.player.x and ac.y == self.player.y:
                if ac.is_win():
                    self.win()
                    return True
                elif ac.is_lose():
                    self.lose(self.player)
                    return True
        return False

    def run(self) -> None:
        """
        Run the Game until it ends or player quits.
        """
        while self._running:
            pygame.time.wait(1000 // FPS)
            self._events()
            self._update()
            self._draw()



    def set_player(self, actor_: Optional[actor.Actor]) -> None:
        """
        Takes an actor and sets that actor to be the player
        """
        self.player = actor_

    def remove_player(self, actor_: actor.Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """
        self._actors.remove(actor_)
        self.player = None

    def _update(self) -> None:
        """
        Check each "Is" tile to find what rules are added and which are removed
        if any, and handle them accordingly.
        """
        self._rules = self.get_rules()
        actual_if_rules = []

        for is_ in self._is:
            block_above_is = self.get_actor(is_.x, is_.y - 1)
            block_under_is = self.get_actor(is_.x, is_.y + 1)
            block_left_is = self.get_actor(is_.x - 1, is_.y)
            block_right_is = self.get_actor(is_.x + 1, is_.y)

            horiz, vertical = is_.update(block_above_is, block_under_is, block_left_is, block_right_is)

            if horiz:
                actual_if_rules.append(horiz)

            if vertical:
                actual_if_rules.append(vertical)

        victory_block_x, victory_block_y = 0, 0
        if len(self._rules) != len(actual_if_rules):
            if len(self._rules) < len(actual_if_rules):
                new_rules = [x for x in actual_if_rules + self._rules if x in actual_if_rules and x not in self._rules]
                self._rules.extend(new_rules)
                for new_rule in new_rules:
                    subject = self.get_character(new_rule.split()[0])
                    attribute = new_rule.split()[1]
                    self.change_property(subject, attribute, "was set")

            else:
                ex_rules = [x for x in actual_if_rules + self._rules if x in self._rules and x not in actual_if_rules]
                self._rules = actual_if_rules
                for deleted_rule in ex_rules:
                    subject = self.get_character(deleted_rule.split()[0])
                    attribute = deleted_rule.split()[1]
                    self.change_property(subject, attribute)
        else:
            difference_new = [x for x in self._rules + actual_if_rules if x in actual_if_rules and x not in self._rules]
            difference_old = [x for x in self._rules + actual_if_rules if x not in actual_if_rules and x in self._rules]
            if difference_new:
                self._rules = actual_if_rules
                subject = self.get_character(difference_old[0].split()[0])
                attribute = difference_old[0].split()[1]
                self.change_property(subject, attribute)
                subject = self.get_character(difference_new[0].split()[0])
                attribute = difference_new[0].split()[1]
                self.change_property(subject, attribute, "was set")

    def change_property(self, subject: Optional[type], attribute: str, comment: str ="was deleted") -> Tuple[str, str]:
        """
        Takes a rule-string, split it and change the attribute of the given subject
        """

        all_our_subjects = [i for i in self._actors if type(i) == subject]

        if len(all_our_subjects) == 1:
            only_one_subject = all_our_subjects[0]

            if comment != "was deleted":
                if attribute == 'isPush':
                    only_one_subject.set_push()

                if attribute == 'isStop':
                    only_one_subject.set_stop()

                if attribute == 'isVictory':
                    only_one_subject.set_win()

                if attribute == 'isYou':
                    self.player = only_one_subject

                if attribute == 'isLose':
                    only_one_subject.set_lose()

            else:
                if attribute == 'isPush':
                    only_one_subject.unset_push()

                if attribute == 'isStop':
                    only_one_subject.unset_stop()

                if attribute == 'isVictory':
                    only_one_subject.unset_win()

                if attribute == 'isYou':
                    only_one_subject.unset_player()

                if attribute == 'isLose':
                    only_one_subject.unset_lose()
        else:
            for sub in all_our_subjects:
                if comment != "was deleted":
                    if attribute == 'isPush':
                        sub._is_push = True

                    if attribute == 'isStop':
                        sub._is_stop = True

                    if attribute == 'isVictory':
                        sub.set_win()

                    if attribute == 'isYou':
                        self.player = sub

                    if attribute == 'isLose':
                        sub.set_lose()

                else:
                    if attribute == 'isPush':
                        sub.unset_push()

                    if attribute == 'isStop':
                        sub.unset_stop()

                    if attribute == 'isVictory':
                        sub.unset_win()

                    if attribute == 'isYou':
                        sub.unset_player()

                    if attribute == 'isLose':
                        sub.unset_lose()

    @staticmethod
    def get_character(subject: str) -> Optional[Type[Any]]:
        """
        Takes a string, returns appropriate class representing that string
        """
        if subject == "Meepo":
            return actor.Meepo
        elif subject == "Wall":
            return actor.Wall
        elif subject == "Rock":
            return actor.Rock
        elif subject == "Flag":
            return actor.Flag
        elif subject == "Bush":
            return actor.Bush
        return None

    def _undo(self) -> None:
        """
        Returns the game to a previous state based on what is at the top of the
        _history stack.
        """
        if not self._history.is_empty():
            old_game = self._history.pop()
            self.set_player(old_game.player)
            self._actors = old_game.get_actors()
            self._actors.append(self.player)
            self._rules = old_game.get_rules()
            self._is = old_game._is

        return


    def _copy(self) -> 'Game':
        """
        Copies relevant attributes of the game onto a new instance of Game.
        Return new instance of game
        """
        game_copy = Game()
        for i in self.get_actors():
            if i != self.player:
            # if act == self.player:
                copy_actor = i.copy()
                game_copy._actors.append(copy_actor)
            if isinstance(i, actor.Is):
                game_copy._is.append(copy_actor)
        game_copy._rules = self._rules[:]
        game_copy.player = self.player.copy()
        return game_copy

    def get_actor(self, x: int, y: int) -> Optional[actor.Actor]:
        """
        Return the actor at the position x,y. If the slot is empty, Return None
        """
        for ac in self._actors:
            if ac.x == x and ac.y == y:
                return ac
        return None

    def win(self) -> None:
        """
        End the game and print win message.
        """
        self._running = False
        print("Congratulations, you won!")

    def lose(self, char: actor.Character) -> None:
        """
        Lose the game and print lose message
        """
        self.remove_player(char)
        print("You lost! But you can have it undone if undo is done :)")


if __name__ == "__main__":
    game = Game()
    # load_map public function
    game.load_map(MAP_PATH)
    game.new()
    game.run()
    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['settings', 'stack', 'actor', 'pygame']
    # })
