from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Game(db.Model):
    name = db.Column(db.String(50), primary_key=True)
    min_players = db.Column(db.Integer())
    max_players = db.Column(db.Integer())

    def __init__(self):
        self.name = ""
        self.min_players = 0
        self.max_players = 0

    def __str__(self):
        return "<name: " + self.name + ", minPlayers: " + str(self.min_players) + ", maxPlayers: " + str(self.max_players) + ">"
    
    def __repr__(self):
        return "<name: " + self.name + ", minPlayers: " + str(self.min_players) + ", maxPlayers: " + str(self.max_players) + ">"