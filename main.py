from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import join_room, leave_room, SocketIO
from string import ascii_uppercase
import random
from classes import event
from classes import allocatorUtil, solution
from classes.game import db, Game

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
app.config['host'] = '0.0.0.0'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///games.db"
socketio = SocketIO(app)
db.init_app(app)
rooms = {}

@app.route('/input-preferences', methods=["POST", "GET"])
def input_preferences():
    preferences = {}
    room = session.get('room')
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    if request.method == "POST":
        for game in session['games']:
            preferences[game] = int(request.form.get(f"{game}-inlineRadioOptions"))

        session['preferenceScores'] = preferences
        return redirect(url_for('room'))

    return render_template("input_preferences.html", games=session['games'], roomcode=session['room'], name=session['name'])

@app.route('/', methods=["POST", "GET"])
def home():
    session.clear()
    games = ["Dune", "Star Realms", "PanAm", "Catan", "MTG"]
    games.sort()

    if request.method == "POST":
        session['isCreator'] = False
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        selectedGames = request.form.getlist("selectedGames")

        if join != False and (not code or len(code) != 4):
            return render_template("home.html", error="Please enter a valid room code.", code=code, name=name)
        room = code
        # Determine if POST request is from join or create
        if create != False: # User pressed "create" button and selected games.
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "games": selectedGames, 'preferences':{}}
            session['isCreator'] = True
        elif code not in rooms: # User attempts to join a room
            return render_template("home.html", error="Room does not exist", len = len(games), games = games, code=code, name=name)

        session['room'] = room
        session['name'] = name
        session['games'] = rooms[room]['games']

        return redirect(url_for('input_preferences'))
    result = [r[0] for r in Game.query.with_entities(Game.name).all()]
    return render_template("home.html", games = result)

@app.route('/room')
def room():
    room = session.get('room')
    

    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))
    return render_template('room.html', name=session['name'], room=session['room'], games=session['games'], preferenceScores = session['preferenceScores'], isCreator = session['isCreator'])

@app.route('/games', methods=['GET', 'POST'])
def show_all():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['minPlayers'] or not request.form['maxPlayers']:
            flash('Please enter all the fields', 'error')
        else:
            game = Game()
            game.name = request.form['name']
            game.min_players = request.form['minPlayers']
            game.max_players = request.form['maxPlayers']
            
            # Insert new or update existing entry by checking DB to see if entry exists first
            existing_game = Game.query.filter_by(name=game.name).first()
            if existing_game is None:
                # Add new entry
                db.session.add(game)
                db.session.commit()
                flash(f'{game.name} Has been succefully added.')
            else:
                # Update existing entry with new fields
                existing_game.name = game.name
                existing_game.min_players = game.min_players
                existing_game.max_players = game.max_players
                db.session.commit()
                flash(f'{game.name} Has been succefully Updated.')
            
            return render_template('show_all.html', games=Game.query.order_by(Game.name).all())

    return render_template('show_all.html', games=Game.query.order_by(Game.name).all())

@app.route('/delete/<name>')
def delete(name):
    game_to_delete = Game.query.get_or_404(name)
    try:
        db.session.delete(game_to_delete)
        db.session.commit()
        return redirect(url_for("show_all"))
    except:
        print(f"\nError deleting game: {game_to_delete}")

@socketio.on("connect")
def connect(auth):
    room = session.get('room')
    name = session.get('name')

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    print(f"{name} has joined the room {room}")
    rooms[room]["members"] += 1
    rooms[room]['preferences'][name] = session.get('preferenceScores')

    socketio.emit("updateRoom", rooms[room]["preferences"], to=room)

"""
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")

    # Remove the user and their preferences from the room
    rooms[room]["preferences"].pop(name)
    socketio.emit("updateRoom", rooms[room]["preferences"], to=room)
    leave_room(room)

    # If the last person has leaves, delete the room
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            print(f"{room} has been deleted")
            del rooms[room]

    print(f"{name} has left the room {room}")
"""
@socketio.on("assign")
def assign():
    sol = solution.Solution()
    myevent = event.Event()
    room = session.get("room")
    myevent.from_room(rooms[room])

    # Comment out the next 3 lines when testing. Makes life a lot easier not having to connect multiple sessions
    solver = allocatorUtil.Solver(myevent)
    sol = solver.check_all_combinations()
    socketio.emit("solution", sol.assignments, to=room)

    # Uncomment when testing.
    #socketio.emit("solution", {"Dune":["Colton","Joel","Adam"], "Star Realms":["Fred", "Jason", "Grace"]}, to=room)

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    
    return code

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', debug=True)