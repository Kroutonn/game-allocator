from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
from string import ascii_uppercase
import random
from classes import event
from classes import allocatorUtil, solution
import csv

games_map = {}

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
app.config['host'] = '0.0.0.0'
socketio = SocketIO(app)

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

    return render_template("home.html", games = list(games_map.keys()))

@app.route('/room')
def room():
    room = session.get('room')
    

    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))
    return render_template('room.html', name=session['name'], room=session['room'], games=session['games'], preferenceScores = session['preferenceScores'], isCreator = session['isCreator'])

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

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    content = {
        "name": session.get("name"),
        "scores": session.get("preferenceScores")
    }

    rooms[room]["messages"].append(content)

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
    with open('data/games.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            game = row[0]
            minPlayer = row[1]
            maxPlayer = row[2]

            games_map[game] = {"min":minPlayer, "max":maxPlayer}

    socketio.run(app, host='0.0.0.0', debug=True)