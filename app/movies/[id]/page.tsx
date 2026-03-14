'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  getMovie,
  getMovieGenres,
  Movie,
  Genre,
  getUserInteractions,
  addInteraction,
  getMovieId
} from '@/lib/api';
import Image from 'next/image';

const styles = {
  page: {
    minHeight: '100vh',
    padding: '3rem 0',
    position: 'relative' as const,
    backgroundColor: '#0a0e1a',
    color: '#ffffff',
  },
  backdrop: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'radial-gradient(circle at top right, rgba(229, 9, 20, 0.15), transparent 60%)',
    zIndex: -1,
  },
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '0 2rem',
  },
  backButton: {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    color: '#ffffff',
    padding: '0.8rem 1.5rem',
    borderRadius: '2rem',
    fontWeight: 700,
    cursor: 'pointer',
    transition: '0.3s',
    marginBottom: '2rem',
  },
  content: {
    display: 'grid',
    gridTemplateColumns: 'minmax(300px, 450px) 1fr',
    gap: '4rem',
  },
  posterContainer: {
    position: 'sticky' as const,
    top: '2rem',
    height: 'fit-content',
  },
  poster: {
    width: '100%',
    height: 'auto',
    borderRadius: '2rem',
    boxShadow: '0 30px 60px rgba(0,0,0,0.7)',
    border: '1px solid rgba(255,255,255,0.1)',
  },
  info: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '2.5rem',
  },
  title: {
    fontSize: '4rem',
    fontWeight: 900,
    lineHeight: 1.1,
    letterSpacing: '-2px',
  },
  meta: {
    display: 'flex',
    gap: '2.5rem',
    flexWrap: 'wrap' as const,
    color: '#7a8ba3',
    fontSize: '1.1rem',
  },
  interactionBar: {
    background: 'rgba(26, 34, 53, 0.6)',
    backdropFilter: 'blur(20px)',
    borderRadius: '1.5rem',
    padding: '2rem',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1.5rem',
  },
  likeContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.5rem',
  },
  likeBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    background: 'none',
    border: '1px solid rgba(255,255,255,0.1)',
    color: '#ffffff',
    padding: '0.75rem 1.5rem',
    borderRadius: '1rem',
    cursor: 'pointer',
    transition: '0.3s',
    fontSize: '1.2rem',
  },
  starContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  star: {
    fontSize: '2rem',
    cursor: 'pointer',
    transition: '0.2s',
  },
  genreTag: {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    color: '#ffffff',
    padding: '0.6rem 1.25rem',
    borderRadius: '3rem',
    fontWeight: 600,
    fontSize: '0.9rem',
    transition: '0.3s',
  },
  description: {
    color: '#b8c5d6',
    lineHeight: 1.8,
    fontSize: '1.2rem',
  },
  externalLinks: {
    display: 'flex',
    gap: '1.5rem',
    marginTop: '3.5rem',
    flexWrap: 'wrap' as const,
  },
  externalBtn: {
    padding: '0.8rem 1.8rem',
    borderRadius: '1.25rem',
    textDecoration: 'none',
    fontWeight: 800,
    fontSize: '1rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    transition: '0.3s all cubic-bezier(0.4, 0, 0.2, 1)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255,255,255,0.1)',
  },
  imdbBtn: {
    backgroundColor: 'rgba(245, 197, 24, 0.15)',
    color: '#f5c518',
    borderColor: 'rgba(245, 197, 24, 0.3)',
  },
  tmdbBtn: {
    backgroundColor: 'rgba(1, 180, 228, 0.15)',
    color: '#01b4e4',
    borderColor: 'rgba(1, 180, 228, 0.3)',
  }
};

export default function MovieDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  // Interaction states
  const [isLiked, setIsLiked] = useState<boolean | null>(null); // true=like, false=dislike, null=none
  const [userRating, setUserRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);

  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) setUser(JSON.parse(savedUser));

    if (params.id) {
      loadMovieData();
    }
  }, [params.id]);

  useEffect(() => {
    if (user && movie) {
      fetchUserInteraction();
    }
  }, [user, movie]);

  const loadMovieData = async () => {
    try {
      setLoading(true);
      const movieId = parseInt(params.id as string);
      const [movieData, genresData] = await Promise.all([
        getMovie(movieId),
        getMovieGenres(movieId).catch(() => [])
      ]);
      setMovie(movieData);
      setGenres(genresData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserInteraction = async () => {
    if (!user || !movie) return;
    try {
      const interactions = await getUserInteractions(user.user_id);
      const mid = getMovieId(movie);
      const current = interactions.find(i => i.movie_id === mid);
      if (current) {
        setIsLiked(current.is_liked);
        setUserRating(current.rating || 0);
      }
    } catch (e) { console.error(e); }
  };

  const handleLike = async (value: boolean) => {
    if (!user) {
      window.dispatchEvent(new CustomEvent('open-auth'));
      return;
    }
    const newValue = isLiked === value ? null : value;
    setIsLiked(newValue);
    try {
      await addInteraction(user.user_id, getMovieId(movie!), newValue === true, userRating);
    } catch (e) { console.error(e); }
  };

  const handleRate = async (rating: number) => {
    if (!user) {
      window.dispatchEvent(new CustomEvent('open-auth'));
      return;
    }
    setUserRating(rating);
    try {
      await addInteraction(user.user_id, getMovieId(movie!), isLiked === true, rating);
    } catch (e) { console.error(e); }
  };

  if (loading) return <div style={{ color: 'white', padding: '100px', textAlign: 'center' }}>Yükleniyor...</div>;
  if (!movie) return <div style={{ color: 'white', padding: '100px', textAlign: 'center' }}>Film bulunamadı.</div>;

  return (
    <main style={styles.page}>
      <div style={styles.backdrop} />
      <div style={styles.container}>
        <button
          onClick={() => {
            sessionStorage.setItem('returnFromDetail', 'true');
            router.push('/');
          }}
          style={styles.backButton}
        >
          ← Geri Dön
        </button>

        <div style={styles.content}>
          <div style={styles.posterContainer}>
            <Image
              src={movie.poster_url || ""}
              alt={movie.title}
              width={450}
              height={675}
              style={styles.poster}
            />
          </div>

          <div style={styles.info}>
            <h1 style={styles.title}>{movie.title}</h1>

            <div style={styles.meta}>
              <span>{movie.release_date?.substring(0, 4)}</span>
              <span>{movie.runtime} Dakika</span>
              <span>{movie.original_language?.toUpperCase()}</span>
              <span style={{ color: '#ffd700' }}>★ {movie.vote_average?.toFixed(1)}</span>
            </div>

            <div style={styles.interactionBar}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={styles.likeContainer}>
                  <button
                    onClick={() => handleLike(true)}
                    style={{
                      ...styles.likeBtn,
                      background: isLiked === true ? 'rgba(255,255,255,0.1)' : 'none',
                      borderColor: isLiked === true ? '#ffffff' : 'rgba(255,255,255,0.1)'
                    }}
                  >
                    👍 {isLiked === true ? 'Beğendin' : 'Beğen'}
                  </button>
                  <button
                    onClick={() => handleLike(false)}
                    style={{
                      ...styles.likeBtn,
                      background: isLiked === false ? 'rgba(229, 9, 20, 0.2)' : 'none',
                      borderColor: isLiked === false ? '#e50914' : 'rgba(255,255,255,0.1)'
                    }}
                  >
                    👎 {isLiked === false ? 'Beğenmedin' : 'Beğenme'}
                  </button>
                </div>

                <div style={styles.starContainer}>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <span
                      key={star}
                      onMouseEnter={() => setHoverRating(star)}
                      onMouseLeave={() => setHoverRating(0)}
                      onClick={() => handleRate(star)}
                      style={{
                        ...styles.star,
                        color: (hoverRating || userRating) >= star ? '#ffd700' : 'rgba(255,255,255,0.1)'
                      }}
                    >
                      ★
                    </span>
                  ))}
                  <span style={{ marginLeft: '1rem', color: '#7a8ba3', fontWeight: 700 }}>{userRating}/5</span>
                </div>
              </div>
            </div>

            <div>
              <h3 style={{ marginBottom: '1rem', color: '#7a8ba3', textTransform: 'uppercase', letterSpacing: '2px', fontSize: '0.9rem' }}>Türler</h3>
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                {genres.map(g => (
                  <span key={g.genre_id} style={styles.genreTag}>{g.genre_name}</span>
                ))}
              </div>
            </div>

            <div>
              <h3 style={{ marginBottom: '1rem', color: '#7a8ba3', textTransform: 'uppercase', letterSpacing: '2px', fontSize: '0.9rem' }}>Özet</h3>
              <p style={styles.description}>{movie.llm_metadata?.split(',').slice(2).join(',') || "Özet bulunamadı."}</p>
            </div>

            <div style={styles.externalLinks}>
              {movie.imdbId && (
                <a
                  href={`https://www.imdb.com/title/tt${movie.imdbId.toString().padStart(7, '0')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ ...styles.externalBtn, ...styles.imdbBtn }}
                  onMouseOver={(e) => { e.currentTarget.style.backgroundColor = 'rgba(245, 197, 24, 0.25)'; e.currentTarget.style.transform = 'translateY(-3px)'; }}
                  onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'rgba(245, 197, 24, 0.15)'; e.currentTarget.style.transform = 'translateY(0)'; }}
                >
                  <span style={{ fontSize: '1.2rem', fontWeight: 900 }}>IMDb</span>
                  <span>Sayfasına Git ➔</span>
                </a>
              )}
              {movie.tmdbId && (
                <a
                  href={`https://www.themoviedb.org/movie/${movie.tmdbId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ ...styles.externalBtn, ...styles.tmdbBtn }}
                  onMouseOver={(e) => { e.currentTarget.style.backgroundColor = 'rgba(1, 180, 228, 0.25)'; e.currentTarget.style.transform = 'translateY(-3px)'; }}
                  onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'rgba(1, 180, 228, 0.15)'; e.currentTarget.style.transform = 'translateY(0)'; }}
                >
                  <span style={{ fontSize: '1.2rem', fontWeight: 900 }}>TMDb</span>
                  <span>Detayları Gör ➔</span>
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
