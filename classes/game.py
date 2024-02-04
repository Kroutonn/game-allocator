class Game():
    def __init__(self):
        self.name = ""
        self.min_players = 0
        self.max_players = 0

    def __str__(self):
        return "<name: " + self.name + ", minPlayers: " + str(self.minPlayers) + ", maxPlayers: " + str(self.maxPlayers) + ">"
    
    def __repr__(self):
        return "<name: " + self.name + ", minPlayers: " + str(self.minPlayers) + ", maxPlayers: " + str(self.maxPlayers) + ">"