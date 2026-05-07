class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []

    def set_exit(self, direction, room):
        self.exits[direction] = room

    def describe(self):
        lines = [f"You are in {self.name}.", self.description]
        if self.items:
            lines.append("You see: " + ", ".join(self.items))
        if self.exits:
            lines.append("Exits: " + ", ".join(self.exits.keys()))
        return "\n".join(lines)


class Player:
    def __init__(self, start_room):
        self.current_room = start_room
        self.inventory = []

    def move(self, direction):
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            return f"You move {direction}."
        return "You cannot go that way."

    def look(self):
        return self.current_room.describe()

    def take(self, item):
        if item in self.current_room.items:
            self.current_room.items.remove(item)
            self.inventory.append(item)
            return f"You take the {item}."
        return f"There is no {item} here."

    def status(self):
        if self.inventory:
            return "Inventory: " + ", ".join(self.inventory)
        return "Inventory: empty"


class Game:
    def __init__(self):
        self.rooms = self.create_world()
        self.player = Player(self.rooms['entrance'])
        self.running = True

    def create_world(self):
        entrance = Room("Goblin Cave Entrance", "A damp tunnel with a faint green glow.")
        hall = Room("Bone Hall", "Old skeletons line the walls and a strange odor fills the air.")
        nest = Room("Goblin Nest", "A mess of stolen trinkets and a sleeping goblin.")
        treasure = Room("Hidden Lair", "A small chamber with a cracked chest in the center.")

        entrance.set_exit('north', hall)
        hall.set_exit('south', entrance)
        hall.set_exit('east', nest)
        hall.set_exit('north', treasure)
        nest.set_exit('west', hall)
        treasure.set_exit('south', hall)

        entrance.items.append('torch')
        hall.items.append('bone')
        nest.items.append('ruby')
        treasure.items.append('gold coin')

        return {
            'entrance': entrance,
            'hall': hall,
            'nest': nest,
            'treasure': treasure,
        }

    def show_help(self):
        return (
            "Commands:\n"
            "  look - observe your surroundings\n"
            "  go <direction> - move north, south, east, or west\n"
            "  take <item> - pick up an item\n"
            "  inventory - check what you carry\n"
            "  quit - leave the adventure"
        )

    def process(self, command):
        command = command.strip().lower()
        if not command:
            return "Type a command."
        parts = command.split()
        verb = parts[0]

        if verb == 'look':
            return self.player.look()
        if verb == 'go' and len(parts) > 1:
            return self.player.move(parts[1])
        if verb == 'take' and len(parts) > 1:
            return self.player.take(' '.join(parts[1:]))
        if verb == 'inventory':
            return self.player.status()
        if verb == 'help':
            return self.show_help()
        if verb == 'quit':
            self.running = False
            return "Goodbye."
        return "I don't understand that command."

    def run(self):
        print("Welcome to the Goblin Body Adventure.")
        print(self.show_help())
        print(self.player.look())

        while self.running:
            command = input('> ')
            response = self.process(command)
            print(response)


if __name__ == '__main__':
    Game().run()
