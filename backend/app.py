from flask import Flask, request, jsonify
from flask_cors import CORS
from game import Game

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

game_instance = None

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/start', methods=['POST'])
def start():
    global game_instance
    data = request.json
    buy_in = data.get('buy_in', 100)
    game_instance = Game(buy_in)
    return jsonify(game_instance.start_hand())

@app.route('/bet', methods=['POST'])
def bet():
    if not game_instance:
        return jsonify({"error": "Game not started"}), 400
    data = request.json
    multiplier = data.get("multiplier", 1)
    result = game_instance.place_bet(multiplier)

    if not result["success"]:
        return jsonify({"error": result["message"]}), 400

    return jsonify(result)


@app.route('/deal_flop', methods=['GET'])
def deal_flop():
    if not game_instance:
        return jsonify({"error": "Game not started"}), 400
    flop = game_instance.deal_flop()
    return jsonify({"flop": flop})

@app.route('/deal_turn_or_river', methods=['GET'])
def deal_turn_or_river():
    if not game_instance:
        return jsonify({"error": "Game not started"}), 400
    card = game_instance.deal_turn_or_river()
    return jsonify({"card": card})

@app.route('/fold', methods=['POST'])
def fold():
    if not game_instance:
        return jsonify({"error": "Game not started"}), 400
    return jsonify(game_instance.fold())

@app.route('/winner', methods=['GET'])
def winner():
    if not game_instance:
        return jsonify({"error": "Game not started"}), 400
    return jsonify(game_instance.determine_winner())

@app.route('/auto_resolve_after_bet', methods=['POST'])
def auto_resolve_after_bet():
    if not game_instance:
        return jsonify({"error": "Game not started"}), 400

    data = request.json
    multiplier = data.get("multiplier", 1)
    bet_result = game_instance.place_bet(multiplier)

    if not bet_result["success"]:
        return jsonify({"error": "Not enough balance"}), 400

    if len(game_instance.community_cards) < 3:
        game_instance.deal_flop()
    while len(game_instance.community_cards) < 5:
        game_instance.deal_turn_or_river()

    result = game_instance.determine_winner()

    return jsonify({
        "player_hand": game_instance.player.hand,
        "dealer_hand": game_instance.dealer.hand,
        "community_cards": game_instance.community_cards,
        "pot": game_instance.pot,
        "balance": result["balance"],
        "winner": result["winner"]
    })

@app.route('/check', methods=['POST'])
def check():
    if not game_instance:
        return jsonify({"error": "Game not started"}), 400
    return jsonify(game_instance.check())

if __name__ == '__main__':
    app.run(debug=True)