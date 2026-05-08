"""
=============================================================
 GOBLIN'S LAST STAND — A Text Adventure
=============================================================
 A text-based adventure from the perspective of GRIX,
 a goblin warrior in a horde facing down a legendary hero.

 --- Developer Split ---
  Dev 1 (Alice)  : class World      — rooms, map, lore
  Dev 2 (Bob)    : class Entity     — combat, stats, items
  Dev 3 (Carol)  : class GameEngine — game loop, UI, story
=============================================================
"""

import random
import textwrap
import time
import sys
import os


# ─────────────────────────────────────────────────────────────
#  DEV 1 — ALICE
#  class World
#  Owns: rooms, map layout, item pickups, environmental lore
# ─────────────────────────────────────────────────────────────

class World:
    """
    Manages the game map: a network of rooms connected by exits.
    Each room has a description, optional items, and neighbours.
    """

    def __init__(self):
        self.rooms = self._build_map()
        self.items = self._build_items()        # room_id -> list of item dicts
        self.current_room_id = "cave_entrance"

    # ── Map construction ──────────────────────────────────────

    def _build_map(self) -> dict:
        """Return a dict of room_id -> room data."""
        return {
            "cave_entrance": {
                "name": "Cave Entrance",
                "short": "The jagged mouth of your horde's lair.",
                "description": (
                    "Torchlight flickers across damp stone walls. The stench of "
                    "unwashed goblins, rotting meat, and crude mushroom-brew fills "
                    "the air. Your horde-brothers grunt and jostle behind you. "
                    "Through the cave mouth you can see grey morning light — and "
                    "somewhere out there, the HERO approaches."
                ),
                "exits": {"north": "rocky_pass", "east": "armory"},
                "enemies_here": False,
            },
            "armory": {
                "name": "The Goblin Armory",
                "short": "Rusted weapons and stolen scraps hang from the walls.",
                "description": (
                    "Broken swords, cracked shields, and sharpened femurs litter "
                    "crude wooden racks. The Horde Smith, Brokk, squints at you "
                    "from beneath a leather apron. 'You goink to fight da hero?' "
                    "he rasps. 'Grab somethin' sharp, ya fool.'"
                ),
                "exits": {"west": "cave_entrance"},
                "enemies_here": False,
            },
            "rocky_pass": {
                "name": "Rocky Pass",
                "short": "A narrow canyon path littered with bones.",
                "description": (
                    "Skulls of previous 'volunteers' line the path. The wind "
                    "howls between the crags. Your horde-brothers are watching "
                    "from the cave. Ahead, in the clearing, you can make out the "
                    "glint of polished armour. The Hero is HERE."
                ),
                "exits": {"south": "cave_entrance", "north": "clearing"},
                "enemies_here": False,
            },
            "clearing": {
                "name": "The Battleground Clearing",
                "short": "An open field stained with old blood.",
                "description": (
                    "The Hero stands in the centre of the clearing, gleaming "
                    "sword raised, cape billowing dramatically in the wind. "
                    "Around you your fellow goblins scatter like roaches. "
                    "The Hero's eyes lock onto YOU. 'Foul creature!' they bellow. "
                    "'Face me and meet your doom!' ... This is it."
                ),
                "exits": {"south": "rocky_pass", "east": "ravine"},
                "enemies_here": True,   # Hero fight triggers here
            },
            "ravine": {
                "name": "The Crumbling Ravine",
                "short": "A treacherous ledge above a long, dark drop.",
                "description": (
                    "Loose rocks crumble under your clawed feet. The ravine "
                    "plunges into darkness below. It's a desperate escape route — "
                    "or a way to flank an overconfident hero."
                ),
                "exits": {"west": "clearing", "north": "shrine"},
                "enemies_here": False,
            },
            "shrine": {
                "name": "Ancient Goblin Shrine",
                "short": "A moss-covered idol of the Great Green Maw.",
                "description": (
                    "Your ancestors carved this idol from a single obsidian "
                    "boulder. The Great Green Maw — goblin god of cunning and "
                    "survival — glares down at you with hollow eyes. "
                    "Offerings of shiny pebbles and chewed bones litter the altar. "
                    "You feel... slightly less likely to die horribly."
                ),
                "exits": {"south": "ravine"},
                "enemies_here": False,
            },
        }

    def _build_items(self) -> dict:
        """Return items available in each room."""
        return {
            "armory": [
                {"name": "Rusty Sword",     "type": "weapon", "bonus": 3,
                 "desc": "Chipped and blood-stained. Still pointy though."},
                {"name": "Cracked Shield",  "type": "armor",  "bonus": 2,
                 "desc": "Half a shield is better than none. Probably."},
                {"name": "Bone Shiv",       "type": "weapon", "bonus": 1,
                 "desc": "Carved from a hero's shin. Lucky charm!"},
            ],
            "shrine": [
                {"name": "Maw's Blessing",  "type": "potion", "bonus": 15,
                 "desc": "A vial of green glow. Smells like swamp and destiny."},
            ],
            "rocky_pass": [
                {"name": "Throwing Rock",   "type": "weapon", "bonus": 1,
                 "desc": "A perfectly round throwing rock. Classic."},
            ],
        }

    # ── Public API ────────────────────────────────────────────

    def current_room(self) -> dict:
        return self.rooms[self.current_room_id]

    def move(self, direction: str) -> tuple[bool, str]:
        """Attempt to move in a direction. Returns (success, message)."""
        exits = self.rooms[self.current_room_id]["exits"]
        if direction not in exits:
            return False, f"You can't go {direction} from here."
        self.current_room_id = exits[direction]
        return True, self.rooms[self.current_room_id]["name"]

    def get_items_here(self) -> list:
        return self.items.get(self.current_room_id, [])

    def remove_item(self, item_name: str):
        items = self.items.get(self.current_room_id, [])
        self.items[self.current_room_id] = [
            i for i in items if i["name"].lower() != item_name.lower()
        ]

    def is_boss_room(self) -> bool:
        return self.rooms[self.current_room_id].get("enemies_here", False)

    def describe_exits(self) -> str:
        exits = self.current_room()["exits"]
        return "Exits: " + ", ".join(f"[{d.upper()}]" for d in exits)


# ─────────────────────────────────────────────────────────────
#  DEV 2 — BOB
#  class Entity
#  Owns: stats, combat resolution, inventory, levelling
# ─────────────────────────────────────────────────────────────

class Entity:
    """
    Represents any combatant — player goblin or the Hero.
    Handles stats, inventory management, and combat logic.
    """

    def __init__(self, name: str, hp: int, attack: int,
                 defense: int, is_player: bool = False):
        self.name       = name
        self.max_hp     = hp
        self.hp         = hp
        self.base_attack  = attack
        self.base_defense = defense
        self.is_player  = is_player
        self.inventory: list[dict] = []
        self.weapon: dict | None = None
        self.armor:  dict | None = None
        self.gold = random.randint(3, 12) if not is_player else 0

    # ── Stats helpers ─────────────────────────────────────────

    @property
    def attack(self) -> int:
        bonus = self.weapon["bonus"] if self.weapon else 0
        return self.base_attack + bonus

    @property
    def defense(self) -> int:
        bonus = self.armor["bonus"] if self.armor else 0
        return self.base_defense + bonus

    def is_alive(self) -> bool:
        return self.hp > 0

    def hp_bar(self, width: int = 20) -> str:
        ratio = max(self.hp, 0) / self.max_hp
        filled = int(ratio * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {max(self.hp,0)}/{self.max_hp}"

    # ── Inventory ─────────────────────────────────────────────

    def pick_up(self, item: dict) -> str:
        """Add item to inventory; auto-equip if better than current."""
        self.inventory.append(item)
        msg = f"You picked up: {item['name']}."
        if item["type"] == "weapon":
            if self.weapon is None or item["bonus"] > self.weapon["bonus"]:
                self.weapon = item
                msg += f" EQUIPPED as weapon! (+{item['bonus']} ATK)"
        elif item["type"] == "armor":
            if self.armor is None or item["bonus"] > self.armor["bonus"]:
                self.armor = item
                msg += f" EQUIPPED as armor! (+{item['bonus']} DEF)"
        elif item["type"] == "potion":
            msg += " (Use with 'use potion' during combat.)"
        return msg

    def use_potion(self) -> tuple[bool, str]:
        potions = [i for i in self.inventory if i["type"] == "potion"]
        if not potions:
            return False, "You have no potions!"
        potion = potions[0]
        self.inventory.remove(potion)
        heal = potion["bonus"]
        self.hp = min(self.hp + heal, self.max_hp)
        return True, f"You quaff the {potion['name']}! Healed {heal} HP. {self.hp_bar()}"

    def show_inventory(self) -> str:
        if not self.inventory:
            return "Your sack is empty (like your future)."
        lines = ["=== Your Sack ==="]
        for item in self.inventory:
            eq = ""
            if item is self.weapon: eq = " [WEAPON]"
            if item is self.armor:  eq = " [ARMOR]"
            lines.append(f"  • {item['name']}{eq} — {item['desc']}")
        lines.append(f"  Weapon ATK bonus: +{self.weapon['bonus'] if self.weapon else 0}")
        lines.append(f"  Armor  DEF bonus: +{self.armor['bonus']  if self.armor  else 0}")
        return "\n".join(lines)

    # ── Combat ────────────────────────────────────────────────

    def calculate_damage(self, target: "Entity") -> int:
        """Raw damage before target defense."""
        raw = self.attack + random.randint(-2, 4)
        return max(raw, 1)

    def take_damage(self, dmg: int) -> int:
        """Apply damage reduced by defense. Returns actual damage taken."""
        reduced = max(dmg - self.defense + random.randint(-1, 2), 1)
        self.hp -= reduced
        return reduced

    def attempt_flee(self) -> bool:
        """50/50 chance to flee, better if low HP."""
        hp_ratio = self.hp / self.max_hp
        chance = 0.4 + (0.3 if hp_ratio < 0.3 else 0)
        return random.random() < chance

    def enemy_turn(self, target: "Entity") -> tuple[str, int]:
        """AI: hero attacks with occasional taunts."""
        taunts = [
            "\"Yield, foul beast!\"",
            "\"Is that all you've got, creature?\"",
            "\"Your kind shall trouble this land no more!\"",
            "\"For the kingdom!\"",
            "\"I've slain dragons — you are NOTHING!\"",
        ]
        taunt = random.choice(taunts) if random.random() < 0.3 else ""
        dmg_raw = self.calculate_damage(target)
        dmg_dealt = target.take_damage(dmg_raw)
        msg = f"{self.name} swings! "
        if taunt:
            msg += f"{taunt} "
        msg += f"Hits for {dmg_dealt} damage."
        return msg, dmg_dealt


# ─────────────────────────────────────────────────────────────
#  DEV 3 — CAROL
#  class GameEngine
#  Owns: game loop, narrative, UI printing, win/lose states
# ─────────────────────────────────────────────────────────────

class GameEngine:
    """
    Drives the game loop, handles player input, narrates events,
    and decides win/lose conditions.
    """

    WIDTH = 60

    def __init__(self):
        self.world  = World()
        self.player = Entity("Grix", hp=30, attack=6, defense=2, is_player=True)
        self.hero   = Entity("The Hero", hp=50, attack=10, defense=4, is_player=False)
        self.hero_defeated = False
        self.boss_fight_started = False
        self.turn_count = 0
        self.running = True

    # ── Formatting helpers ────────────────────────────────────

    def _hr(self, char="─"):
        print(char * self.WIDTH)

    def _box(self, title: str):
        self._hr()
        print(f"  {title}")
        self._hr()

    def _wrap(self, text: str):
        for line in textwrap.wrap(text, width=self.WIDTH - 4):
            print(f"  {line}")

    def _pause(self, seconds: float = 0.6):
        time.sleep(seconds)

    def _print_status(self):
        room = self.world.current_room()
        print(f"\n  📍 {room['name']}")
        print(f"  ❤️  Grix HP: {self.player.hp_bar()}")
        if self.boss_fight_started and self.hero.is_alive():
            print(f"  ⚔️  Hero HP: {self.hero.hp_bar()}")
        print(f"  {self.world.describe_exits()}")

    # ── Intro / Outro ─────────────────────────────────────────

    def _intro(self):
        os.system("cls" if os.name == "nt" else "clear")
        self._hr("═")
        print("       GOBLIN'S LAST STAND")
        print("  A Text Adventure in Three Classes")
        self._hr("═")
        self._wrap(
            "You are GRIX — scrawniest, sneakiest goblin in the "
            "Bonecrusher Horde. Today the Horde Boss pointed a "
            "gnarled finger at you and said: 'YOU. Go fight da hero.' "
            "It was not a request."
        )
        print()
        self._wrap(
            "Your goal: survive, find equipment, maybe even defeat "
            "The Hero. Or at least die in a way that impresses someone."
        )
        self._hr("═")
        print("\n  COMMANDS: north/south/east/west  |  look  |  take  ")
        print("            inventory              |  stats |  help  ")
        print("  IN COMBAT: attack | flee | use potion")
        self._hr("═")
        input("\n  Press ENTER to start your glorious / terrible adventure...\n")

    def _victory(self):
        self._hr("═")
        print("\n  🏆  VICTORY! (Sort of.)")
        self._wrap(
            "The Hero collapses, cursing dramatically. You stand over "
            "them, breathing hard, covered in your own blood and theirs. "
            "From the cave mouth, the horde erupts in wet, chaotic cheering. "
            "Brokk the Smith shouts: 'I MADE DA SWORD THAT DID IT!' "
            "(He did not.) You are, against all odds, a goblin legend."
        )
        print(f"\n  Survived {self.turn_count} turns. Well done, little monster.\n")
        self._hr("═")

    def _defeat(self):
        self._hr("═")
        print("\n  💀  DEFEATED.")
        self._wrap(
            "The Hero stands over your crumpled form, wiping their blade. "
            "They mutter something about justice and light before striding "
            "toward the cave. Your horde-brothers are already fleeing "
            "out the back. At least you bought them twelve seconds."
        )
        print(f"\n  Lasted {self.turn_count} turns. Grix will be remembered.")
        print("  (He will not be remembered.)\n")
        self._hr("═")

    # ── Combat loop ───────────────────────────────────────────

    def _combat(self):
        """Full turn-based combat encounter with the Hero."""
        self._box("⚔️  COMBAT BEGINS!")
        self._wrap(
            "The Hero raises their gleaming sword. Time slows. "
            "Your knees are shaking but your grip on your weapon holds."
        )
        print()

        while self.player.is_alive() and self.hero.is_alive():
            self._hr()
            print(f"  Grix:     {self.player.hp_bar()}")
            print(f"  The Hero: {self.hero.hp_bar()}")
            self._hr()
            print("  [attack]  [use potion]  [flee]")
            action = input("  > ").strip().lower()

            # ── Player action ──
            if action in ("attack", "a", "hit", "fight"):
                dmg_raw  = self.player.calculate_damage(self.hero)
                dmg_dealt = self.hero.take_damage(dmg_raw)
                goblin_taunts = [
                    "You screech and lunge!", "You bite AND stab!",
                    "You attack from a slightly lower angle!",
                    "You hurl dirt then stab!", "You go for the kneecap!"
                ]
                self._wrap(f"{random.choice(goblin_taunts)} Hit for {dmg_dealt} damage!")
                self._pause(0.4)

            elif action in ("use potion", "potion", "p", "heal", "drink"):
                ok, msg = self.player.use_potion()
                self._wrap(msg)
                if not ok:
                    continue          # Don't use hero's turn if nothing happened
                self._pause(0.4)

            elif action in ("flee", "run", "escape", "f"):
                if self.player.attempt_flee():
                    self._wrap("You dart between the hero's legs and bolt south!")
                    self.world.move("south")
                    self.boss_fight_started = False
                    return
                else:
                    self._wrap("The Hero cuts off your escape! You stumble back.")
                    self._pause(0.4)
            else:
                self._wrap("(Unknown action — you hesitate!)")

            self._pause(0.3)

            # ── Hero's turn ──
            if self.hero.is_alive():
                msg, _ = self.hero.enemy_turn(self.player)
                self._wrap(msg)
                self._pause(0.5)

            self.turn_count += 1

        # ── End of combat ──
        if not self.hero.is_alive():
            self.hero_defeated = True
            self._wrap(
                "The Hero staggers and falls! Their sword clatters on the stone. "
                "You DID IT. YOU ACTUALLY DID IT."
            )
        elif not self.player.is_alive():
            pass   # handled in main loop

    # ── Command handlers ──────────────────────────────────────

    def _cmd_look(self):
        room = self.world.current_room()
        self._box(f"👁  {room['name']}")
        self._wrap(room["description"])
        items = self.world.get_items_here()
        if items:
            print()
            print("  Items here:")
            for item in items:
                print(f"    • {item['name']} — {item['desc']}")
        print(f"\n  {self.world.describe_exits()}")

    def _cmd_take(self, args: list[str]):
        if not args:
            print("  Take what? (e.g. 'take rusty sword')")
            return
        item_name = " ".join(args)
        items_here = self.world.get_items_here()
        match = next((i for i in items_here
                      if i["name"].lower() == item_name.lower()), None)
        if not match:
            # Fuzzy: check if any item name contains the query
            match = next((i for i in items_here
                          if item_name.lower() in i["name"].lower()), None)
        if not match:
            print(f"  There's no '{item_name}' here.")
            return
        msg = self.player.pick_up(match)
        self.world.remove_item(match["name"])
        self._wrap(msg)

    def _cmd_move(self, direction: str):
        ok, msg = self.world.move(direction)
        if ok:
            print(f"\n  → Moving to: {msg}")
            self._pause(0.3)
            room = self.world.current_room()
            self._wrap(room["short"])
            # Trigger combat if entering boss room
            if self.world.is_boss_room() and not self.hero_defeated:
                self.boss_fight_started = True
                self._wrap(
                    "\nThe Hero spots you. There's nowhere to hide. "
                    "It's time to fight!"
                )
                self._pause(1.0)
                self._combat()
        else:
            print(f"  ✗ {msg}")

    def _cmd_stats(self):
        p = self.player
        self._box("📊 GRIX — STATUS")
        print(f"  HP:      {p.hp_bar()}")
        print(f"  Attack:  {p.attack}  (base {p.base_attack}"
              f"{f' + {p.weapon[\"bonus\"]} weapon' if p.weapon else ''})")
        print(f"  Defense: {p.defense}  (base {p.base_defense}"
              f"{f' + {p.armor[\"bonus\"]} armor' if p.armor else ''})")
        print(f"  Weapon:  {p.weapon['name'] if p.weapon else 'Bare claws'}")
        print(f"  Armor:   {p.armor['name']  if p.armor  else 'Rags and hope'}")
        print(f"  Turns survived: {self.turn_count}")

    def _cmd_help(self):
        self._box("❓ HELP")
        cmds = [
            ("north / south / east / west", "Move between rooms"),
            ("look",                        "Examine the current room"),
            ("take <item name>",            "Pick up an item"),
            ("inventory  (or 'inv')",       "Check your sack"),
            ("stats",                       "View Grix's stats"),
            ("help",                        "Show this help"),
            ("quit",                        "Give up (coward)"),
            ("--- IN COMBAT ---",           ""),
            ("attack",                      "Strike the Hero"),
            ("use potion",                  "Drink a healing potion"),
            ("flee",                        "Attempt to escape (50/50)"),
        ]
        for cmd, desc in cmds:
            if desc:
                print(f"  {cmd:<32} {desc}")
            else:
                print(f"\n  {cmd}")

    # ── Main loop ─────────────────────────────────────────────

    def run(self):
        self._intro()
        self._cmd_look()

        while self.running:
            # ── Win condition ──
            if self.hero_defeated:
                self._victory()
                break

            # ── Lose condition ──
            if not self.player.is_alive():
                self._defeat()
                break

            self._print_status()
            try:
                raw = input("\n  > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n  (Grix slinks away into the dark...)")
                break

            if not raw:
                continue

            tokens = raw.split()
            cmd    = tokens[0]
            args   = tokens[1:]

            self.turn_count += 1

            if cmd in ("north", "n", "south", "s", "east", "e", "west", "w"):
                dirs = {"n": "north", "s": "south", "e": "east", "w": "west"}
                self._cmd_move(dirs.get(cmd, cmd))

            elif cmd == "look":
                self._cmd_look()

            elif cmd == "take":
                self._cmd_take(args)

            elif cmd in ("inventory", "inv", "i"):
                print(self.player.show_inventory())

            elif cmd == "stats":
                self._cmd_stats()

            elif cmd == "help":
                self._cmd_help()

            elif cmd in ("quit", "exit", "q"):
                print("  Grix slips into a crack in the rock. Gone forever.")
                break

            else:
                print(f"  Grix doesn't understand '{raw}'. Type 'help' for commands.")


# ─────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    game = GameEngine()
    game.run()