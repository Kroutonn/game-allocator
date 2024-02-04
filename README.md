# game-allocator
Takes in an assortment of board games, players, and their preference ratings to play each game and assigns groups to games.

## Use
`pip install -r dependencies.txt`
`python main.py -f filepath.txt`

Run the file main.py directly, with an accompanying pref.txt file that gives players' preferences for games in the following format:

\[game name 1\]:\[minimum player requirement\]:\[maximum player requirement\]

\[game name 2\]:\[minimum player requirement\]:\[maximum player requirement\]

...

\* <- divider symbol needed between list of games and list of player preferences.

\[player 1\]| \[game name 1\]:\[rating\], \[game name 2\]:\[rating\], ...

\[player 2\]| \[game name 1\]:\[rating\], \[game name 2\]:\[rating\], ...

...

Whitespace is ignored and higher numbers mean a greater player preference, usually on a scale of 5 to 1. A smaller range may be more appropriate when fewer choices are offered.
This format can also be seen in the existing examples of pref.txt and the tests/ files.
