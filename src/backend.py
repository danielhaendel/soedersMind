from flask import Flask, session, request
import random

app = Flask(__name__)

# Wichtig: für Sessions braucht Flask einen Secret Key
app.secret_key = "super-secret-key"

def init_random_number():
    # Generiere eine Zufallszahl zwischen 0 und 100
    random_number = random.randint(0, 100)

    # Speichere sie in der Session
    session["target_number"] = random_number

    return f"Neue Zufallszahl wurde generiert und in der Session gespeichert: {random_number}"

def guess_number(guessedNumber):

    if "target_number" not in session:
        return "Es wurde noch keine Zahl generiert. Bitte zuerst /init aufrufen."
    
    try:
        guess = int(guessedNumber)
    except ValueError:
        return "Ungültige Eingabe. Bitte gib eine ganze Zahl an."

    if guess is None:
        return "Bitte gib eine Zahl zum Raten an."


    # Vergleich mit gespeicherter Zahl
    correctNumber = session["target_number"]

    if guess == correctNumber:
        return "🎉 Erfolg! Du hast die richtige Zahl erraten!"
    elif guess > correctNumber:
        return "Du bist drüber!"
    else:
        return "Du bist drunter!"