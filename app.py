import os
import flask_sqlalchemy
from flask import Flask, jsonify
from website import create_app


app = create_app()

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)