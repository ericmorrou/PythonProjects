from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'games.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class VideoGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    developer = db.Column(db.String(100))
    release_year = db.Column(db.Integer)
    genre = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'developer': self.developer,
            'release_year': self.release_year,
            'genre': self.genre
        }

# Data initialization
with app.app_context():
    db.create_all()

# Routes
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Welcome to the VideoGame API',
        'endpoints': {
            'list_games': '/games',
            'create_game': '/games',
            'get_game': '/games/<id>',
            'update_game': '/games/<id>',
            'delete_game': '/games/<id>'
        }
    }), 200

@app.route('/games', methods=['GET'])
def get_games():
    games = VideoGame.query.all()
    return jsonify([g.to_dict() for g in games]), 200

@app.route('/games/<int:id>', methods=['GET'])
def get_game(id):
    game = VideoGame.query.get_or_404(id)
    return jsonify(game.to_dict()), 200

@app.route('/games', methods=['POST'])
def create_game():
    data = request.get_json()
    if not data or not 'title' in data:
        return jsonify({'error': 'Title is required'}), 400
    
    new_game = VideoGame(
        title=data['title'],
        developer=data.get('developer'),
        release_year=data.get('release_year'),
        genre=data.get('genre')
    )
    db.session.add(new_game)
    db.session.commit()
    return jsonify(new_game.to_dict()), 201

@app.route('/games/<int:id>', methods=['PUT'])
def update_game(id):
    game = VideoGame.query.get_or_404(id)
    data = request.get_json()
    
    game.title = data.get('title', game.title)
    game.developer = data.get('developer', game.developer)
    game.release_year = data.get('release_year', game.release_year)
    game.genre = data.get('genre', game.genre)
    
    db.session.commit()
    return jsonify(game.to_dict()), 200

@app.route('/games/<int:id>', methods=['DELETE'])
def delete_game(id):
    game = VideoGame.query.get_or_404(id)
    db.session.delete(game)
    db.session.commit()
    return jsonify({'message': 'Game deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
