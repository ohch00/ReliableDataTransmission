from flask import Flask
import os

app = Flask(__name__)


@app.route('/')
def root():
    return None


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(port=port)