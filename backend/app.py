from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

app = Flask(__name__)

# Load pre-trained Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create a sample database (run once)
def create_database():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Insert sample data (run once)
def insert_sample_data():
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, description, price) VALUES (?, ?, ?)',
                 ('Wireless Earbuds', 'Noise-cancelling earbuds with 20-hour battery life', 99.99))
    conn.execute('INSERT INTO products (name, description, price) VALUES (?, ?, ?)',
                 ('Bluetooth Headphones', 'Over-ear headphones with built-in mic', 79.99))
    conn.execute('INSERT INTO products (name, description, price) VALUES (?, ?, ?)',
                 ('Wired Earbuds', 'Basic earbuds with 3.5mm jack', 19.99))
    conn.commit()
    conn.close()

# API endpoint to recommend cheaper products
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    target_description = data['description']
    target_price = float(data['price'])

    # Fetch all products from the database
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()

    # Convert product descriptions to embeddings
    product_descriptions = [product['description'] for product in products]
    embeddings = model.encode(product_descriptions)

    # Encode the target description
    target_embedding = model.encode([target_description])

    # Compute cosine similarity
    similarities = cosine_similarity(target_embedding, embeddings).flatten()

    # Filter cheaper products
    recommendations = []
    for i, product in enumerate(products):
        if product['price'] < target_price:
            recommendations.append({
                'name': product['name'],
                'description': product['description'],
                'price': product['price'],
                'similarity': float(similarities[i])
            })

    # Sort by similarity
    recommendations.sort(key=lambda x: x['similarity'], reverse=True)

    return jsonify(recommendations)

if __name__ == '__main__':
    create_database()
    insert_sample_data()  # Run once to populate the database
    app.run(debug=True)
