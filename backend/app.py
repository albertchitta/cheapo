from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

# Insert sample data (run once)from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from amazon.api import AmazonAPI  # For Amazon Product Advertising API
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load pre-trained Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Amazon API credentials (replace with your own)
AMAZON_ACCESS_KEY = 'your-access-key'
AMAZON_SECRET_KEY = 'your-secret-key'
AMAZON_ASSOCIATE_TAG = 'your-associate-tag'

# Initialize Amazon API
amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG)

# Function to search for products on Amazon
def search_amazon_products(keywords):
    try:
        products = amazon.search(Keywords=keywords, SearchIndex='All')
        return [{
            'name': product.title,
            'description': product.title,  # Use title as description
            'price': product.price_and_currency[0],
            'url': product.detail_page_url
        } for product in products]
    except Exception as e:
        print(f"Error fetching products from Amazon: {e}")
        return []

# API endpoint to recommend cheaper products
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    target_description = data['description']
    target_price = float(data['price'])

    # Search for products on Amazon
    products = search_amazon_products(target_description)

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
                'url': product['url'],
                'similarity': float(similarities[i])
            })

    # Sort by similarity
    recommendations.sort(key=lambda x: x['similarity'], reverse=True)

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
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
