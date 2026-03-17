"use client";

import { useEffect, useState } from "react";
import { useInView } from "react-intersection-observer";
import { fetchMoviesAction } from "@/app/actions";
import { Movie, getMovieId } from "@/lib/api";
import MovieCard from "@/components/MovieCard";

interface InfiniteMovieListProps {
  initialMovies: Movie[];
  onAdd: (m: Movie) => Promise<void>;
  onRemove: (m: Movie) => Promise<void>;
  isWatched: (m: Movie) => boolean;
}

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '2rem',
    padding: '2rem 4%',
  },
  loadingContainer: {
    padding: '2rem',
    textAlign: 'center' as const,
    color: '#b8c5d6',
    fontSize: '1.2rem',
    fontWeight: 600,
  },
};

export default function InfiniteMovieList({ 
  initialMovies, 
  onAdd, 
  onRemove, 
  isWatched 
}: InfiniteMovieListProps) {
  const [movies, setMovies] = useState<Movie[]>(initialMovies);
  const [offset, setOffset] = useState(initialMovies.length);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const { ref, inView } = useInView({
    threshold: 0.1,
  });

  useEffect(() => {
    if (inView && !loading && hasMore) {
      loadMoreMovies();
    }
  }, [inView, loading, hasMore]);

  const loadMoreMovies = async () => {
    setLoading(true);
    try {
      const newMovies = await fetchMoviesAction(offset, 24);
      if (newMovies.length === 0) {
        setHasMore(false);
      } else {
        // Dedup if necessary, though SQL OFFSET/LIMIT should handle it
        setMovies((prev) => {
          const prevIds = new Set(prev.map(m => getMovieId(m)));
          const filtered = newMovies.filter(m => !prevIds.has(getMovieId(m)));
          return [...prev, ...filtered];
        });
        setOffset((prev) => prev + newMovies.length);
      }
    } catch (error) {
      console.error("Failed to load more movies:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <div style={styles.grid}>
        {movies.map((movie: Movie) => (
          <MovieCard
            key={getMovieId(movie)}
            movie={movie}
            onAdd={onAdd}
            onRemove={onRemove}
            isWatched={isWatched(movie)}
          />
        ))}
      </div>
      
      {hasMore && (
        <div ref={ref} style={styles.loadingContainer}>
          {loading ? "🍿 Yeni filmler getiriliyor..." : "Daha fazlası için kaydırın"}
        </div>
      )}
      
      {!hasMore && movies.length > 0 && (
        <div style={styles.loadingContainer}>
          ✨ Tüm filmleri keşfettiniz!
        </div>
      )}
    </section>
  );
}
