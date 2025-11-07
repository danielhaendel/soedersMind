from src import create_app

app = create_app()

# Ensure a secret key is set even if Flask config has None
if not app.secret_key:
    app.secret_key = "change-me"


if __name__ == "__main__":
    app.run(debug=True)
