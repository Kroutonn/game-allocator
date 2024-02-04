
#Internal Imports
from classes.game import Game
from classes.player import Player

#External Imports
import pandas as pd

class Event():
    def __init__(self):
        self.players = []
        self.games = []

    # Load from standard text file
    # Expected format:
    # gameName:minPlayers:maxPlayers
    # * <= deliminator between games and players
    # player|game1:preferenceScore,gamenN:preferenceScore
    def from_text_file(self, filepath):
        with open(filepath, 'r') as file:
            while line := file.readline().strip():
                if line == "*":
                    break
                items = line.split(":")
                game = Game()
                game.name = items[0]
                game.min_players = int(items[1])
                game.max_players = int(items[2])
                self.games.append(game)

            while line := file.readline().strip():
                items = line.split("|")
                player = Player()
                player.name = items[0]
                given_prefs = items[1].split(",")
                for game_rating in given_prefs:
                    game_to_rating = game_rating.split(":")
                    player.preference_scores[game_to_rating[0].strip()] = int(game_to_rating[1])
                self.players.append(player)

    def to_data_frame(self):
        game_names = []
        for game in self.games:
            game_names.append(game.name)
        
        df = pd.DataFrame(columns=game_names)
        for player in self.players:
            df.loc[player.name] = player.preference_scores

        return df
    
    def get_min_player(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game.min_players
            
    def get_max_player(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game.max_players
            
    def get_game_names(self):
        names = list(game.name for game in self.games)
        return names
    
    def average_min_players(self):
        int(sum(game.min_players for game in self.games)/len(self.games))

        return round(sum(game.min_players for game in self.games)/len(self.games))