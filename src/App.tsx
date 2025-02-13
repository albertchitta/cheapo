import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [recommendations, setRecommendations] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/recommend", {
        description: description,
        price: price,
      });
      setRecommendations(response.data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
  };

  return (
    <div className="App">
      <h1>Cheaper Product Recommender</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Product Description:</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Product Price:</label>
          <input
            type="number"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
          />
        </div>
        <button type="submit">Find Cheaper Alternatives</button>
      </form>

      <h2>Recommendations</h2>
      <ul>
        {recommendations.map((product, index) => (
          <li key={index}>
            <h3>{product.name}</h3>
            <p>{product.description}</p>
            <p>Price: ${product.price.toFixed(2)}</p>
            <p>Similarity: {product.similarity.toFixed(2)}</p>
            <a href={product.url} target="_blank" rel="noopener noreferrer">
              Buy Now
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
