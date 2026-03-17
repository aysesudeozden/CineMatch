const { createPool } = require('@vercel/postgres');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.join(__dirname, '.env') });

const pool = createPool({
  connectionString: process.env.DATABASE_URL
});

async function test() {
  console.log("Connecting to:", process.env.DATABASE_URL ? "URL present" : "URL MISSING");
  try {
    const moviesRes = await pool.query('SELECT * FROM movies LIMIT 1');
    console.log("Movies columns:", Object.keys(moviesRes.rows[0] || {}));
    
    const genresRes = await pool.query('SELECT * FROM movie_genres LIMIT 1');
    console.log("Movie-Genres columns:", Object.keys(genresRes.rows[0] || {}));
  } catch (err) {
    console.error("DB Error:", err);
  } finally {
    process.exit();
  }
}

test();
