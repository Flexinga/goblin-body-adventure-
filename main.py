#   rohit-> World  (map, rooms, items)
#   susuja   -> Entity (stats, combat, inventory)
#   steve -> GameEngine (loop, input, printing)


import random

class World:
    # rohit owns this
    # Stores rooms as a dict, each room has:
    # name, description, exits

    def __init__(self):

        # Room map
        self.rooms = {

            "start": {
                "name": "Goblin Camp",
                "description": "A filthy cave filled with bones and broken weapons.",
                "exits": {
                    "east": "forest"
                }
            },

            "forest": {
                "name": "Dark Forest",
                "description": "Tall dead trees surround you. Strange noises echo around.",
                "exits": {
                    "west": "start",
                    "north": "river",
                    "east": "ruins"
                }
            },

            "river": {
                "name": "Frozen River",
                "description": "An icy river blocks part of the path.",
                "exits": {
                    "south": "forest"
                }
            },

            "ruins": {
                "name": "Ancient Ruins",
                "description": "Broken stone pillars and ancient goblin carvings remain here.",
                "exits": {
                    "west": "forest",
                    "east": "castle"
                }
            },

            "castle": {
                "name": "Hero's Castle",
                "description": "The Hero waits inside the ruined throne room.",
                "exits": {
                    "west": "ruins"
                }
            }
        }

        # Items placed in rooms
        self.items = {

            "start": [
                {
                    "name": "Rusty Dagger",
                    "type": "weapon",
                    "attack_bonus": 2
                }
            ],

            "forest": [
                {
                    "name": "Healing Potion",
                    "type": "potion",
                    "heal_amount": 30
                }
            ],

            "river": [
                {
                    "name": "Iron Armour",
                    "type": "armour",
                    "defense_bonus": 3
                }
            ],

            "ruins": [
                {
                    "name": "Hero Slayer Axe",
                    "type": "weapon",
                    "attack_bonus": 5
                },

                {
                    "name": "Mega Potion",
                    "type": "potion",
                    "heal_amount": 50
                }
            ],

            "castle": []
        }

        # Starting room
        self.current_room_id = "start"

    def current_room(self) -> dict:

        # Return current room data
        return self.rooms[self.current_room_id]

    def move(self, direction: str) -> tuple:

        room = self.current_room()

        # Check if movement is possible
        if direction in room["exits"]:

            new_room_id = room["exits"][direction]

            self.current_room_id = new_room_id

            return (True, self.rooms[new_room_id]["name"])

        return (False, "You cannot go that way.")

    def get_items_here(self) -> list:

        # Return items in current room
        return self.items.get(self.current_room_id, [])

    def remove_item(self, item_name: str):

        room_items = self.get_items_here()

        for item in room_items:

            if item["name"].lower() == item_name.lower():

                room_items.remove(item)
                return

    def is_boss_room(self) -> bool:

        # Boss room = castle
        return self.current_room_id == "castle"

    def describe_exits(self) -> str:

        exits = self.current_room()["exits"].keys()

        # Format exits nicely
        return "Exits: " + ", ".join(exits)

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
        self.armour = None    # equipped armour dict or None

    @property
    def attack(self) -> int:
        bonus = self.weapon["attack_bonus"] if self.weapon else 0
        return self.base_attack + bonus

    @property
    def defense(self) -> int:
        bonus = self.armour["defense_bonus"] if self.armour else 0
        return self.base_defense + bonus

    def is_alive(self) -> bool:
        return self.hp > 0

    def hp_bar(self) -> str:
        bar_length = 20
        filled = int((self.hp / self.max_hp) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"[{bar}] {self.hp}/{self.max_hp}"

    def pick_up(self, item: dict) -> str:
        self.inventory.append(item)
        msg = f"You picked up {item['name']}."

        item_type = item.get("type")

        if item_type == "weapon":
            if self.weapon is None or item["attack_bonus"] > self.weapon["attack_bonus"]:
                self.weapon = item
                msg += f" You equip it as your weapon (+{item['attack_bonus']} ATK)."

        elif item_type == "armour":
            if self.armour is None or item["defense_bonus"] > self.armour["defense_bonus"]:
                self.armour = item
                msg += f" You equip it as your armour (+{item['defense_bonus']} DEF)."

        return msg

    def use_potion(self) -> tuple:
        # Find first potion in inventory
        for item in self.inventory:
            if item.get("type") == "potion":
                self.inventory.remove(item)
                heal = item.get("heal_amount", 30)
                old_hp = self.hp
                self.hp = min(self.hp + heal, self.max_hp)
                actual_heal = self.hp - old_hp
                return (True, f"You drink the {item['name']} and recover {actual_heal} HP. ({self.hp}/{self.max_hp})")

        return (False, "You have no potions!")

    def show_inventory(self) -> str:
        if not self.inventory:
            return "Your inventory is empty."

        lines = ["Inventory:"]
        for item in self.inventory:
            item_type = item.get("type", "misc")
            if item_type == "weapon":
                lines.append(f"  - {item['name']} [Weapon, +{item['attack_bonus']} ATK]")
            elif item_type == "armour":
                lines.append(f"  - {item['name']} [Armour, +{item['defense_bonus']} DEF]")
            elif item_type == "potion":
                lines.append(f"  - {item['name']} [Potion, +{item.get('heal_amount', 30)} HP]")
            else:
                lines.append(f"  - {item['name']}")

        equipped = []
        if self.weapon:
            equipped.append(f"Weapon: {self.weapon['name']}")
        if self.armour:
            equipped.append(f"Armour: {self.armour['name']}")
        if equipped:
            lines.append("Equipped: " + ", ".join(equipped))

        return "\n".join(lines)

    def calculate_damage(self, target: "Entity") -> int:
        # Small variance so combat isn't totally deterministic
        variance = random.randint(-2, 2)
        return max(1, self.attack + variance)

    def take_damage(self, dmg: int) -> int:
        # Defense reduces damage, always at least 1 gets through
        actual = max(1, dmg - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def attempt_flee(self) -> bool:
        # 40% chance to successfully flee
        return random.random() < 0.4

    def enemy_turn(self, target: "Entity") -> tuple:
        # Small chance enemy does a heavy blow
        if random.random() < 0.15:
            dmg = self.calculate_damage(target) * 2
            actual = target.take_damage(dmg)
            return (
                f"{self.name} unleashes a powerful strike for {actual} damage! ({target.hp}/{target.max_hp} HP)",
                actual
            )
        else:
            dmg = self.calculate_damage(target)
            actual = target.take_damage(dmg)
            return (
                f"{self.name} attacks you for {actual} damage! ({target.hp}/{target.max_hp} HP)",
                actual
            )


class GameEngine:
    # stevie boi owns this
    # Creates World and two Entitys (player + hero)
    # Runs the main loop, handles all printing and input

    def __init__(self):
        self.world = World()

        # Player information, starts weaker, will find items to beat hero
        self.player = Entity(
            "Grix the Frail Goblin", 
            hp=60, 
            attack=13, 
            defense=4, 
            is_player=True
        )

        # The "final boss"
        self.hero = Entity(
            "The Hell-Bringing Hero", 
            hp=100, 
            attack=20, 
            defense=8
        )

        self.hero_defeated = False

        self.turn_count = 0

    def run(self):

        # Introduction
        print("~" * 50)
        print(" THE GOBLINS REVENGE ")
        print("~" * 50)
        print("You have been given a mission by your unruly ruler, the goblin-pig hybrig Nonag...")
        print("The letter, in disgustingly neat handwriting, reads 'HUNT DOWN AND KILL THE HERO' ")
        print("You must search across the lands, collect what is needed, and survive")
        print("Failure will result in death")
        print(" ")

        self._cmd_help()

        # Main Loop
        while True:
            
            # Loss Condition
            if not self.player.is_alive():
                self._defeat()
                break

            # Win Condition
            if self.hero_defeated:
                self._victory()
                break

            room = self.world.current_room()

            # Room Information
            print("\n" + "-" * 50)
            print(f"You are in {room['name']}")
            print(room['description'])
            print(self.world.describe_exits())

            # Room Items
            items = self.world.get_items_here()

            if items:
                print("You see the following items:")
                for item in items:
                    print(f"- {item['name']}")
            
            #Player Input
            print("\nWhat will you do?")
            command = input("> ").strip().lower()

            if not command:
                continue

            parts = command.split()
            cmd = parts[0]
            args = parts[1:]

            # Movement handling
            if cmd in ["north", "south", "east", "west"]:
                self._cmd_move(cmd)

            elif cmd == "look":
                self._cmd_look()

            elif cmd == "take":
                self._cmd_take(args)
            
            elif cmd == "inventory":
                print(self.player.show_inventory())

            elif cmd == "stats":
                self._cmd_stats()

            # Begin the fight in the boss room
            elif cmd == "fight":

                if self.world.is_boss_room():
                    self._combat()
                else:
                    print("Calm down, there's no one here to fight!")
            
            # Heal w/ a potion 
            elif cmd == "potion":
                success, msg = self.player.use_potion()
                print(msg)

            elif cmd == "help":
                self._cmd_help()    
            
            elif cmd == "quit":
                print("Coward. You have failed your mission.")
                break 

            else:
                print("Unknown command.")
            
            self.turn_count += 1

    def _combat(self):
        
        print("\nStart the Battle!")
        print(f"{self.hero.name} blocks your path!")
        
        # Combat Loop
        while self.player.is_alive() and self.hero.is_alive():
            
            #Display HP Bars
            print("\n" + "-" * 40)
            print(f"{self.player.name}: {self.player.hp_bar()}")
            print(f"{self.hero.name}: {self.hero.hp_bar()}")

            print("\nChoose your action:")
            print("1. Attack")
            print("2. Use Potion")
            print("3. Attempt to Flee")

            choice = input("> ").strip()

            # Attack

            if choice == "1":

                dmg = self.player.calculate_damage(self.hero)
                actual_dmg = self.hero.take_damage(dmg)

                print(
                    f"You attack {self.hero.name} for {actual_dmg} damage! "
                    f"({self.hero.hp} HP left)"
                )

                # Hero Defeated
                if not self.hero.is_alive():

                    print(f"You have defeated {self.hero.name}!")
                    self.hero_defeated = True
                    return
                
            # Potion 
            elif choice == "2":

                success, msg = self.player.use_potion()
                print(msg)

                if not success:
                    continue
            
            # Flee
            elif choice == "3":

                if self.player.attempt_flee():
                    print("You successfully fled back to the previous room!")
                    return
                
                else:
                    print("Flee attempt failed! The fight continues.")
            
            else:
                print("Invalid choice, try again.")
                continue
            
            # Hero's Turn
            if self.hero.is_alive:

                msg, dmg = self.hero.enemy_turn(self.player)
                print(msg)

                if not self.player.is_alive():
                    print("You have been defeated by the hero...")
                    return

    def _cmd_look(self): 

        # Show room description again
        room = self.world.current_room()

        print("|n" + room["name"])
        print(room["description"])

        items = self.world.get_items_here()

        if items:

            print("You see the following items:")

            for item in items:
                print(f"- {item['name']}")
        
        print(self.world.describe_exits())
    
    def _cmd_take(self, args):

        # Prevents empty take command
        if not args:
            print("Take what?")
            return

        item_name = " ".join(args).lower()

        items = self.world.get_items_here()

        # Search room for item
        for item in items:
            
            if item["name"].lower() == item_name:
                
                self.world.remove_item(item_name)

                result = self.player.pick_up(item)

                print(result)
                return
        
        print("No such item here.")

    def _cmd_move(self, direction): 

        # Ask to move player
        success, msg = self.world.move(direction)

        if success:
            print(f"You move {direction} to {msg}.")
        
        else:
            print(msg)

    def _cmd_stats(self):

        print("\n" + "-" * 40)
        print(" GRIX'S STATS ")
        print("-" * 40)

        print(f"Name: {self.player.name}")
        print(f"HP: {self.player.hp}/{self.player.max_hp}")
        print(f"Attack: {self.player.attack}")
        print(f"Defense: {self.player.defense}")

        # Display equipped weapon
        if self.player.weapon:
            print(f"Equipped Weapon: {self.player.weapon['name']}")

        else:
            print("Equipped Weapon: None") 

        # Display equipped armour
        if self.player.armour:
            print(f"Equipped Armour: {self.player.armour['name']}")

        else:
            print("Equipped Armour: None")
 
    def _cmd_help(self):

         # List all commands
        print("\nCommands:")
        print(" north/south/east/west - move")
        print(" look - inspect room")
        print(" take <item> - pick up item")
        print(" inventory - show inventory")
        print(" stats - show goblin stats")
        print(" potion - use healing potion")
        print(" fight - fight the Hero")
        print(" help - show commands")
        print(" quit - quit game")

    def _victory(self):

        # Ending if player wins
        print("\n" +"~" * 50)
        print(" VICTORY ")
        print("~" * 50)
        print("The Hero collapses before you.")
        print("You return to the Nonag")
        print("with the Hero's sword as proof.")
        print("The goblin kingdom celebrates")
        print("your victory for a generation, until you are wiped out by global warming...")
        print("~" * 50)

    def _defeat(self): 
        
        # Ending if player loses
        print("\n" + "~" * 50)
        print(" DEFEAT ")
        print("~" * 50)
        print("Your journey ends in failure.")
        print("The Hero survives...")
        print("and the Nonag is fuming, what a sad demise")
        print("The goblin kingdom mourns your loss, but quickly forgets you as they are too busy partying!")
        print("~" * 50)

if __name__ == "__main__":

    game = GameEngine()
    game.run()
