import os
import flask_sqlalchemy
from flask import Flask, jsonify
from website import create_app


app = create_app()
@app.route('/api', methods=['GET'])
def api():
    # Vytvoření JSON odpovědi
    response = {"organization": "Student Cyber Games"}
    # Vrácení odpovědi jako JSON
    return jsonify(response)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)