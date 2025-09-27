from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__)

choices = ["rock", "paper", "scissors"]

# 2nd-order Markov chain: history of (move1, move2) -> next move counts
markov_chain = {}

# Keep track of last two moves
history = []

# New state variable for the round count
round_count = 0


def predict_player_move():
    """
    Predicts the player's next move based on a weighted random choice
    from the Markov chain.
    """
    if len(history) < 2:
        return random.choice(choices)

    state = tuple(history[-2:])
    if state not in markov_chain or not markov_chain[state]:
        return random.choice(choices)

    total_count = sum(markov_chain[state].values())
    if total_count == 0:
        return random.choice(choices)

    moves = list(markov_chain[state].keys())
    weights = list(markov_chain[state].values())

    return random.choices(moves, weights=weights, k=1)[0]


def counter_move(predicted_move):
    """Picks the move that beats the predicted player move."""
    if predicted_move == "rock":
        return "paper"
    elif predicted_move == "paper":
        return "scissors"
    else:  # predicted_move == "scissors"
        return "rock"


@app.route('/')
def home():
    """Serves the main HTML page."""
    return render_template('index.html')


@app.route("/play", methods=["POST"])
def play():
    """Handles a single round of the game."""
    global history, markov_chain, round_count

    # Check if the game has reached the round limit
    if round_count >= 10:
        return jsonify({"message": "Game Over. Please reset to play again.", "gameOver": True})

    data = request.json
    player_choice = data.get("move")

    if player_choice not in choices:
        return jsonify({"error": "Invalid choice"}), 400

    if len(history) >= 2:
        state = tuple(history[-2:])
        if state not in markov_chain:
            markov_chain[state] = {"rock": 0, "paper": 0, "scissors": 0}
        markov_chain[state][player_choice] += 1

    history.append(player_choice)
    round_count += 1

    predicted_next_move = predict_player_move()
    cpu_choice = counter_move(predicted_next_move)

    if player_choice == cpu_choice:
        result = "It's a TIE!"
    elif (player_choice == "rock" and cpu_choice == "scissors") or \
         (player_choice == "paper" and cpu_choice == "rock") or \
         (player_choice == "scissors" and cpu_choice == "paper"):
        result = "You WIN this round!"
    else:
        result = "You LOSE this round!"

    return jsonify({
        "playerChoice": player_choice,
        "cpuChoice": cpu_choice,
        "result": result,
        "roundCount": round_count,
        "gameOver": round_count >= 10
    })


@app.route("/reset", methods=["POST"])
def reset():
    """Resets the game memory (Markov chain + history)."""
    global history, markov_chain, round_count
    history = []
    markov_chain = {}
    round_count = 0
    return jsonify({"message": "Game reset successful"})


if __name__ == "__main__":
    app.run(debug=True)