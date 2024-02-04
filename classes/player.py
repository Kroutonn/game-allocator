class Player():
    def __init__(self):
        self.name = ""
        self.preference_scores = dict()

    def __str__(self):
        return self.name + ":" + str(self.preference_scores)
    
    def __repr__(self):
        return self.name + ":" + str(self.preference_scores)