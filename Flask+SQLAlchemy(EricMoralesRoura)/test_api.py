import unittest
import json
from app import app, db, VideoGame

class VideoGameApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_game(self):
        response = self.client.post('/games', json={
            'title': 'The Legend of Zelda',
            'developer': 'Nintendo',
            'release_year': 1986,
            'genre': 'Adventure'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('The Legend of Zelda', response.get_data(as_text=True))

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('Welcome to the VideoGame API', data['message'])

    def test_get_games(self):
        self.client.post('/games', json={'title': 'Game 1'})
        response = self.client.get('/games')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data), 1)

    def test_get_single_game(self):
        post_response = self.client.post('/games', json={'title': 'Game 2'})
        game_id = json.loads(post_response.get_data(as_text=True))['id']
        response = self.client.get(f'/games/{game_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Game 2', response.get_data(as_text=True))

    def test_update_game(self):
        post_response = self.client.post('/games', json={'title': 'Old Title'})
        game_id = json.loads(post_response.get_data(as_text=True))['id']
        response = self.client.put(f'/games/{game_id}', json={'title': 'New Title'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('New Title', response.get_data(as_text=True))

    def test_delete_game(self):
        post_response = self.client.post('/games', json={'title': 'To Delete'})
        game_id = json.loads(post_response.get_data(as_text=True))['id']
        response = self.client.delete(f'/games/{game_id}')
        self.assertEqual(response.status_code, 200)
        # Verify it's gone
        get_response = self.client.get(f'/games/{game_id}')
        self.assertEqual(get_response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
