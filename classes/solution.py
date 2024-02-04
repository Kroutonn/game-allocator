class Solution:
    def __init__(self):
        self.assignments = {}
        self.total_score = 0

    def add_assignment(self, game, player):
        if game not in self.assignments:
            self.assignments[game] = [player]
        else:
            self.assignments[game].append(player)

    def __str__(self):
        return str(self.total_score) + ": " + str(self.assignments)
    
    def __repr__(self):
        return str(self.total_score) + ": " + str(self.assignments)