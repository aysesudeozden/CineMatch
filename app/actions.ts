"use server";

import { createPool } from "@vercel/postgres";
import { Movie } from "@/lib/api";

const pool = createPool({
  connectionString: process.env.POSTGRES_URL || process.env.DATABASE_URL
});

export async function fetchMoviesAction(offset: number = 0, limit: number = 20) {
  try {
    // Neon.tech / Vercel Postgres query
    const { rows } = await pool.sql<Movie>`
      SELECT * FROM movies 
      ORDER BY "popularity" DESC NULLS LAST
      LIMIT ${limit} OFFSET ${offset}
    `;
    
    return rows;
  } catch (error) {
    console.error("Failed to fetch movies:", error);
    return [];
  }
}
