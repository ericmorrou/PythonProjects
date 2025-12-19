# Flask VideoGame API

This project implements a REST API using Flask and SQLAlchemy for CRUD operations on a `VideoGame` database.

## Prerequisites

- Python 3.x

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Flask server:
```bash
python app.py
```
The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

| Method | Endpoint | Description | Body (JSON) |
|--------|----------|-------------|-------------|
| GET | `/games` | List all games | - |
| GET | `/games/<id>` | Get game details | - |
| POST | `/games` | Create a new game | `{"title": "...", "developer": "...", "release_year": 2024, "genre": "..."}` |
| PUT | `/games/<id>` | Update a game | `{"title": "..."}` (partial updates allowed) |
| DELETE | `/games/<id>` | Delete a game | - |

## Testing

Run the automated test suite:
```bash
python test_api.py
```

## GitHub

(You should upload this project to your GitHub repository and submit the link as requested).
