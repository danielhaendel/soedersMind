from flask import send_from_directory
from src import create_app

app = create_app()

<<<<<<< HEAD
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
=======
# Ensure a secret key is set even if Flask config has None
if not app.secret_key:
    app.secret_key = "change-me"
>>>>>>> dev


if __name__ == "__main__":
    app.run(debug=True)
