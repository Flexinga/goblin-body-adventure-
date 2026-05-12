#   rohit-> World  (map, rooms, items)
#   susuja   -> Entity (stats, combat, inventory)
#   steve -> GameEngine (loop, input, printing)


import random


class World:
    # rohit owns this
    # Stores rooms as a dict, each room has: name, description, exits, items
    # exits = {"north": "room_id", ...}

    def __init__(self):
        self.rooms = {}           # populated in _build_map
        self.items = {}           # room_id -> [item, ...]
        self.current_room_id = "start"
        raise NotImplementedError("Alice: fill this in")

    def current_room(self) -> dict:
        raise NotImplementedError

    def move(self, direction: str) -> tuple:
        # returns (True, room_name) or (False, error_msg)
        raise NotImplementedError

    def get_items_here(self) -> list:
        raise NotImplementedError

    def remove_item(self, item_name: str):
        raise NotImplementedError

    def is_boss_room(self) -> bool:
        raise NotImplementedError

    def describe_exits(self) -> str:
        raise NotImplementedError


class Entity:
    # susuja owns this
    # Covers player AND enemies — hero is also an Entity

    def __init__(self, name: str, hp: int, attack: int, defense: int, is_player=False):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.base_attack = attack
        self.base_defense = defense
        self.is_player = is_player
        self.inventory = []
        self.weapon = None   # equipped weapon dict or None
        self.armor = None    # equipped armor dict or None

    @property
    def attack(self) -> int:
        raise NotImplementedError

    @property
    def defense(self) -> int:
        raise NotImplementedError

    def is_alive(self) -> bool:
        raise NotImplementedError

    def hp_bar(self) -> str:
        raise NotImplementedError

    def pick_up(self, item: dict) -> str:
        # add to inventory, auto-equip if better, return message
        raise NotImplementedError

    def use_potion(self) -> tuple:
        # (True, msg) or (False, msg)
        raise NotImplementedError

    def show_inventory(self) -> str:
        raise NotImplementedError

    def calculate_damage(self, target: "Entity") -> int:
        raise NotImplementedError

    def take_damage(self, dmg: int) -> int:
        # applies defense, returns actual damage taken
        raise NotImplementedError

    def attempt_flee(self) -> bool:
        raise NotImplementedError

    def enemy_turn(self, target: "Entity") -> tuple:
        # returns (message, damage_dealt)
        raise NotImplementedError


class GameEngine:
    # stevie boi owns this
    # Creates World and two Entitys (player + hero)
    # Runs the main loop, handles all printing and input

    def __init__(self):
        self.world = World()
        self.player = Entity("Grix", hp=30, attack=6, defense=2, is_player=True)
        self.hero = Entity("The Hero", hp=50, attack=10, defense=4)
        self.hero_defeated = False
        self.turn_count = 0

    def run(self):
        # main loop: print status, get input, dispatch command
        # exits on win/lose/quit
        

    def _combat(self):
        # turn-based loop: player acts, then hero acts
        # ends when someone dies or player flees
        

    def _cmd_look(self): 
        self.
        self. 

    def _cmd_take(self, args): 
    def _cmd_move(self, direction): 
    def _cmd_stats(self): 
    def _cmd_help(self): 
    def _victory(self): 
    def _defeat(self): 


if __name__ == "__main__":

    game = GameEngine()
    game.run()