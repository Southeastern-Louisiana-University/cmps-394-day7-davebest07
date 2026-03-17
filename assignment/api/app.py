from flask import Flask, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Database connection parameters from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'testdb')

def get_db_connection():
    """Establish a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def wait_for_db():
    """Wait for the database to be ready"""
    max_attempts = 30
    for i in range(max_attempts):
        try:
            conn = get_db_connection()
            conn.close()
            logging.info("Successfully connected to database!")
            return True
        except Exception as e:
            logging.warning(f"Attempt {i+1}/{max_attempts}: Database not ready - {e}")
            time.sleep(2)
    
    logging.error("Could not connect to database after maximum attempts")
    raise Exception("Database connection failed")

def init_db():
    """Initialize the database with sample data"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        
        # Insert sample data if table is empty
        cur.execute('SELECT COUNT(*) FROM messages')
        if cur.fetchone()[0] == 0:
            cur.execute('''
                INSERT INTO messages (title, content) VALUES
                ('Hello', 'Hello, World!'),
                ('Welcome', 'Welcome to the Python API')
            ''')
        
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Database initialized successfully!")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages from the database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT id, title, content FROM messages')
        messages = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': messages
        })
    except Exception as e:
        logging.error(f"Error fetching messages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 503

if __name__ == '__main__':
    # Wait for database to be ready
    wait_for_db()
    
    # Initialize database
    init_db()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
