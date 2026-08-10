import sys
import os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

match_state = {
    "player1": {"name": "", "score": 501, "legs": 0, "visits": 0, "on_nine": False},
    "player2": {"name": "", "score": 501, "legs": 0, "visits": 0, "on_nine": False},
    "turn": 1,
    "format": "",
    "stage": "",
    "subtext": "",
    "history": []
}

SCOREBOARD_PAGE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Scoreboard OBS</title>
    <style>
        body { margin: 0; padding: 0; width: 1920px; height: 1080px; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; overflow: hidden; }
        .scoreboard { position: absolute; top: 40px; left: 40px; width: 550px; background: #0d1a2d; border-radius: 4px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.8); border: 1px solid #1a365d; color: white; }
        .sb-top { display: flex; justify-content: space-between; align-items: center; padding: 6px 12px; background: #08101c; font-size: 13px; font-weight: 700; text-transform: uppercase; color: #8fa3c7; letter-spacing: 0.5px; }
        .sb-top-right { display: flex; gap: 20px; font-size: 12px; }
        .player-row { position: relative; display: flex; align-items: center; height: 52px; background: #102038; border-bottom: 2px solid #8b1e3f; }
        .player-row:last-of-type { border-bottom: none; }
        .player-row.active { background: #152a4a; }
        .player-name { flex-grow: 1; padding-left: 15px; font-size: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .active-dot { width: 8px; height: 8px; background: #e6235c; border-radius: 50%; margin-right: 10px; opacity: 0; }
        .player-row.active .active-dot { opacity: 1; }
        .nine-badge { width: 22px; height: 22px; background: #e6235c; color: white; font-size: 12px; font-weight: 900; display: flex; align-items: center; justify-content: center; border-radius: 3px; margin-right: 10px; opacity: 0; transition: opacity 0.3s ease; }
        .nine-badge.show { opacity: 1; }
        .box-legs { width: 44px; height: 38px; background: #ffffff; color: #000; font-size: 20px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin-right: 6px; border-radius: 2px; }
        .box-score { width: 70px; height: 38px; background: #ffffff; color: #000; font-size: 22px; font-weight: 900; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-family: 'Consolas', monospace; border-radius: 2px; }
        .sb-bottom { background: #08101c; padding: 7px 12px; font-size: 12px; font-weight: 600; color: #8fa3c7; letter-spacing: 0.5px; border-top: 1px solid #1a365d; }
    </style>
</head>
<body>
    <div class="scoreboard">
        <div class="sb-top">
            <div id="format-text"></div>
            <div class="sb-top-right">
                <span id="stage-text"></span>
                <span>LEGS</span>
                <span>PTS</span>
            </div>
        </div>

        <div class="player-row" id="row-p1">
            <div class="player-name" id="name-p1"></div>
            <div class="nine-badge" id="badge-p1">9</div>
            <div class="active-dot"></div>
            <div class="box-legs" id="legs-p1">0</div>
            <div class="box-score" id="score-p1">501</div>
        </div>

        <div class="player-row" id="row-p2">
            <div class="player-name" id="name-p2"></div>
            <div class="nine-badge" id="badge-p2">9</div>
            <div class="active-dot"></div>
            <div class="box-legs" id="legs-p2">0</div>
            <div class="box-score" id="score-p2">501</div>
        </div>

        <div class="sb-bottom" id="subtext-display"></div>
    </div>

    <script>
        function pollScoreboard() {
            fetch('/get_state')
                .then(res => res.json())
                .then(state => {
                    document.getElementById('format-text').innerText = state.format;
                    document.getElementById('stage-text').innerText = state.stage;
                    document.getElementById('subtext-display').innerText = state.subtext;
                    document.getElementById('name-p1').innerText = state.player1.name;
                    document.getElementById('legs-p1').innerText = state.player1.legs;
                    document.getElementById('score-p1').innerText = state.player1.score;
                    document.getElementById('name-p2').innerText = state.player2.name;
                    document.getElementById('legs-p2').innerText = state.player2.legs;
                    document.getElementById('score-p2').innerText = state.player2.score;

                    const badge1 = document.getElementById('badge-p1');
                    if (state.player1.on_nine) { badge1.classList.add('show'); } else { badge1.classList.remove('show'); }
                    const badge2 = document.getElementById('badge-p2');
                    if (state.player2.on_nine) { badge2.classList.add('show'); } else { badge2.classList.remove('show'); }

                    const row1 = document.getElementById('row-p1');
                    const row2 = document.getElementById('row-p2');
                    if (state.turn === 1) {
                        row1.classList.add('active'); row2.classList.remove('active');
                    } else {
                        row2.classList.add('active'); row1.classList.remove('active');
                    }
                });
        }
        setInterval(pollScoreboard, 300);
        pollScoreboard();
    </script>
</body>
</html>
"""

@app.route('/scoreboard')
def scoreboard():
    return render_template_string(SCOREBOARD_PAGE)

@app.route('/get_state')
def get_state():
    return jsonify(match_state)

@app.route('/update_match', methods=['POST'])
def update_match():
    data = request.json
    match_state["format"] = data.get("format", match_state["format"])
    match_state["stage"] = data.get("stage", match_state["stage"])
    match_state["subtext"] = data.get("subtext", match_state["subtext"])
    match_state["player1"]["name"] = data.get("p1_name", match_state["player1"]["name"])
    match_state["player2"]["name"] = data.get("p2_name", match_state["player2"]["name"])
    return jsonify(match_state)

@app.route('/score_visit', methods=['POST'])
def score_visit():
    data = request.json
    points = int(data.get("points", 0))
    if 0 <= points <= 180:
        current = "player1" if match_state["turn"] == 1 else "player2"
        match_state["history"].append({
            "p1_score": match_state["player1"]["score"],
            "p2_score": match_state["player2"]["score"],
            "p1_legs": match_state["player1"]["legs"],
            "p2_legs": match_state["player2"]["legs"],
            "p1_visits": match_state["player1"]["visits"],
            "p2_visits": match_state["player2"]["visits"],
            "turn": match_state["turn"]
        })
        match_state[current]["visits"] += 1
        new_score = match_state[current]["score"] - points
        if new_score < 0 or new_score == 1:
            match_state["turn"] = 2 if match_state["turn"] == 1 else 1
        elif new_score == 0:
            match_state[current]["legs"] += 1
            match_state["player1"]["score"] = 501
            match_state["player2"]["score"] = 501
            match_state["player1"]["visits"] = 0
            match_state["player2"]["visits"] = 0
            match_state["turn"] = 2 if match_state["turn"] == 1 else 1
        else:
            match_state[current]["score"] = new_score
            match_state["turn"] = 2 if match_state["turn"] == 1 else 1

        for p in ["player1", "player2"]:
            v = match_state[p]["visits"]
            s = match_state[p]["score"]
            if v == 1: match_state[p]["on_nine"] = (s <= 350)
            elif v == 2: match_state[p]["on_nine"] = (s <= 170)
            else: match_state[p]["on_nine"] = False
    return jsonify(match_state)

@app.route('/undo', methods=['POST'])
def undo():
    if match_state["history"]:
        last = match_state["history"].pop()
        match_state["player1"]["score"] = last["p1_score"]
        match_state["player2"]["score"] = last["p2_score"]
        match_state["player1"]["legs"] = last["p1_legs"]
        match_state["player2"]["legs"] = last["p2_legs"]
        match_state["player1"]["visits"] = last["p1_visits"]
        match_state["player2"]["visits"] = last["p2_visits"]
        match_state["turn"] = last["turn"]
        for p in ["player1", "player2"]:
            v = match_state[p]["visits"]
            s = match_state[p]["score"]
            if v == 1: match_state[p]["on_nine"] = (s <= 350)
            elif v == 2: match_state[p]["on_nine"] = (s <= 170)
            else: match_state[p]["on_nine"] = False
    return jsonify(match_state)

@app.route('/reset_match', methods=['POST'])
def reset_match():
    match_state["player1"]["score"] = 501
    match_state["player1"]["legs"] = 0
    match_state["player1"]["visits"] = 0
    match_state["player1"]["on_nine"] = False
    match_state["player2"]["score"] = 501
    match_state["player2"]["legs"] = 0
    match_state["player2"]["visits"] = 0
    match_state["player2"]["on_nine"] = False
    match_state["turn"] = 1
    match_state["history"] = []
    return jsonify(match_state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
