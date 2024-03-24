#Internal Imports
from classes.solution import Solution

#External Imports
import pandas as pd
from ortools.linear_solver import pywraplp
from itertools import combinations
import texttable

class Solver:
    def __init__(self, event):
        self.event = event
        self.complete_scores_df = event.to_data_frame() # Dataframe used as the score matrix with each row being a game and each column being a player's preference score
        self.scores_for_subset_df = pd.DataFrame # A subset of games used if there are more games in the pool than will be played.
        self.decision_variables = {}
        self.cp_solver = pywraplp.Solver.CreateSolver("SCIP")
        self.player_counts = dict()
        self.best_solution = Solution()
        self.total_time = 0
        self.total_iterations = 0
        
        # This determines how many games will be used to assign players to, by taking the minimum between number of games and the floor of players divided by games.
        self.game_subset_size = min(len(event.games), len(event.players) // event.average_min_players())

    # The meat of the work is here setting up the linear programing problem and constraints
    def _setup_problem(self):
        # Need to set up decision variables x[p,g] which is an array of 0-1 variables with 1 being if a player is assigned to a game.
        self.decision_variables = {}

        for player in self.scores_for_subset_df.index:
            for game in self.scores_for_subset_df.columns:
                self.decision_variables[player, game] = self.cp_solver.BoolVar(f"x[{self.scores_for_subset_df.index.get_loc(player)},{self.scores_for_subset_df.columns.get_loc(game)}]")

        # Setup Decision Criteria
        # Criterial Number 1: Each game needs a number of players assigned to it between the min and max player count provided
        # Name  |   g1  |   g2  |
        # _______________________
        #   p1  |   1   |   0   |  
        #   p2  |   0   |   1   |
        #   p3  |   0   |   1   |
        #   p4  |   1   |   0   |
        #           ^ sum between min/max of game
        for game in self.scores_for_subset_df.columns:
            self.cp_solver.Add(
                self.cp_solver.Sum(1*[self.decision_variables[player, game] for player in self.scores_for_subset_df.index])
                <= self.event.get_max_player(game)
            )

            self.cp_solver.Add(
                self.cp_solver.Sum(1*[self.decision_variables[player, game] for player in self.scores_for_subset_df.index]) 
                >= self.event.get_min_player(game)
            )

        # Criteria Number 2: Each player should only be assigned to 1 game
        # Name  |   g1  |   g2  |
        # _______________________
        #   p1  |   1   |   0   |   <= sum = 1
        #   p2  |   0   |   1   |
        #   p3  |   0   |   1   |
        #   p4  |   1   |   0   |
        for player in self.scores_for_subset_df.index:
            self.cp_solver.Add(
                self.cp_solver.Sum([self.decision_variables[player, game] for game in self.scores_for_subset_df.columns]) == 1
        )
            
        # Objective
        # Goal is to minimize the preference scores for a game and meet the conditions detailed above. Lower preference rating means that person would prefer to play that game
        objective_terms = []
        
        for player in self.scores_for_subset_df.index:
            for game in self.scores_for_subset_df.columns:
                objective_terms.append(self.decision_variables[player, game] * self.scores_for_subset_df.loc[player][game])
        
        self.cp_solver.Maximize(self.cp_solver.Sum(objective_terms))
        
    # This method requires the solver to be poperly setup. This runs the solver and checks to see if a solution was found and updates the best solution if needed
    def _solve_problem(self):
        status = self.cp_solver.Solve()
        current_solution = Solution()
        self.total_time += self.cp_solver.wall_time()
        self.total_iterations += self.cp_solver.iterations()

        if (status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE) and self.cp_solver.Objective().Value() > self.best_solution.total_score:
            current_solution.total_score = self.cp_solver.Objective().Value()

            for game in self.scores_for_subset_df.columns:
                for player in self.scores_for_subset_df.index:
                    self._check_assignment(current_solution, game, player)

            self.best_solution = current_solution
    
    # Simple method to check if a player is assigned to a game by checking in the decision variable matrix. 1 if assigned, 0 if not
    # If assigned, add that assignment to our current solution.
    def _check_assignment(self, solution, game, player):
        if self.decision_variables[player, game].solution_value() > 0.5:
            solution.add_assignment(game, player)

    def check_all_combinations(self):
        # Solve
        print(f"Solving with {self.cp_solver.SolverVersion()}")

        # ran in to some issues with particular problem sets when trying determining game_subset_size by players/avg_min_player_count, so adding +/- 1 to that to provide a little
        # wiggle room. Probably a better way to dynamically handle how many games are needed, but this works.
        game_combos = []
        game_combos.extend(combinations(self.event.get_game_names(), self.game_subset_size))
        game_combos.extend(combinations(self.event.get_game_names(), self.game_subset_size - 1))
        game_combos.extend(combinations(self.event.get_game_names(), self.game_subset_size + 1))

        # Generate a list of all game combinations meeting our game count requirement and attempt to solve for each combination, keeping only the best
        for i in game_combos:
             self.scores_for_subset_df = self.complete_scores_df[list(i)]
             self._setup_problem()
             self._solve_problem()

        if self.best_solution.total_score > 0:
            self.best_solution
            return self.best_solution
        else:
            print("No solution found, hopefully it's not an error in the code somewhere along the way. Good luck finding that!")

    def print_solution(self):
        print('Run Statistics:')
        table = texttable.Texttable()
        table.add_row(['Total Score', 'Total Time', 'Total Iterations'])
        table.add_row([str(self.best_solution.total_score), str(self.total_time), str(self.total_iterations)])

        print('\n')
        print('Results:')
        table = texttable.Texttable()
        table.add_row(['Game', 'Players'])
        for game, players in self.best_solution.assignments.items():
            table.add_row([game, ' '.join(players)])
        print(table.draw())