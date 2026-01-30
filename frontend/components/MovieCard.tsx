'use client';

import { Movie, getMovieId } from '@/lib/api';
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';

interface MovieCardProps {
  movie: Movie;
  onAdd?: (m: Movie) => void;
  onRemove?: (m: Movie) => void;
  isWatched?: boolean;
}

const styles = {
  card: {
    background: '#1a2235',
    borderRadius: '1.25rem',
    overflow: 'hidden',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    cursor: 'pointer',
    border: '1px solid #2a3548',
    height: '420px',
    width: '230px',
    display: 'flex',
    flexDirection: 'column' as const,
    position: 'relative' as const,
  },
  poster: {
    position: 'relative' as const,
    width: '100%',
    aspectRatio: '2/3',
    overflow: 'hidden',
    background: '#151b2e',
  },
  placeholder: {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '3rem',
    background: 'linear-gradient(135deg, #151b2e, #242d45)',
    color: '#3d4b6e',
  },
  overlay: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(to top, rgba(10, 14, 26, 0.9) 0%, transparent 60%)',
    display: 'flex',
    flexDirection: 'column' as const,
    justifyContent: 'flex-end',
    padding: '1rem',
    opacity: 0,
    transition: 'opacity 0.3s ease',
  },
  rating: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.4rem',
    background: 'rgba(255, 215, 0, 0.9)',
    padding: '0.3rem 0.6rem',
    borderRadius: '0.4rem',
    fontWeight: 800,
    fontSize: '0.8rem',
    color: '#000000',
    marginBottom: '0.5rem',
    width: 'fit-content',
  },
  info: {
    padding: '1rem',
    flex: 1,
    display: 'flex',
    flexDirection: 'column' as const,
    position: 'relative' as const,
  },
  title: {
    fontSize: '0.95rem',
    fontWeight: 700,
    marginBottom: '0.5rem',
    paddingRight: '2rem', // Artı işareti için yer aç
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap' as const,
    lineHeight: 1.3,
    color: '#ffffff',
    display: 'block',
  },
  metadata: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    color: '#7a8ba3',
    fontSize: '0.75rem',
    marginTop: '0.25rem',
  },
  langBadge: {
    textTransform: 'uppercase' as const,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: '0.1rem 0.4rem',
    borderRadius: '0.3rem',
    fontSize: '0.65rem',
    fontWeight: 700,
    color: '#ffffff',
  },
  addToListBtn: {
    position: 'absolute' as const,
    top: '1rem',
    right: '0.75rem',
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.2rem',
    fontWeight: 700,
    cursor: 'pointer',
    transition: '0.2s',
    border: 'none',
    boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
    zIndex: 10,
  }
};

export default function MovieCard({ movie, onAdd, onRemove, isWatched }: MovieCardProps) {
  const [imageError, setImageError] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const posterUrl = movie.poster_url || '';
  const ratingData = movie.vote_average || movie.avg_rating || 0;
  const movieId = getMovieId(movie);
  const lang = movie.original_language || 'en';

  let year = '';
  if (movie.release_date) {
    try {
      if (typeof movie.release_date === 'string') {
        year = movie.release_date.substring(0, 4);
      } else if (movie.release_date instanceof Date) {
        year = movie.release_date.getFullYear().toString();
      } else if (movie.release_date.$date) {
        year = new Date(movie.release_date.$date).getFullYear().toString();
      }
    } catch {
      year = '';
    }
  }

  return (
    <div
      style={{
        ...styles.card,
        transform: isHovered ? 'translateY(-10px)' : 'translateY(0)',
        boxShadow: isHovered ? '0 30px 60px rgba(0,0,0,0.8)' : '0 10px 30px rgba(0,0,0,0.4)',
        borderColor: isHovered ? '#e50914' : '#2a3548',
        zIndex: isHovered ? 50 : 1,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Link href={`/movies/${movieId}`} style={{ textDecoration: 'none', display: 'block' }}>
        <div style={styles.poster}>
          {!imageError && posterUrl ? (
            <Image
              src={posterUrl}
              alt={movie.title}
              fill
              sizes="230px"
              style={{ objectFit: 'cover' }}
              onError={() => setImageError(true)}
            />
          ) : (
            <div style={styles.placeholder}>
              <span>🎬</span>
            </div>
          )}

          <div style={{
            ...styles.overlay,
            opacity: isHovered ? 1 : 0,
          }}>
            <div style={styles.rating}>
              <span>★</span>
              <span>{ratingData > 0 ? ratingData.toFixed(1) : 'NR'}</span>
            </div>
          </div>
        </div>

        <div style={styles.info}>
          <h3 style={styles.title}>{movie.title}</h3>

          {onAdd && (
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                isWatched ? onRemove?.(movie) : onAdd?.(movie);
              }}
              style={{
                ...styles.addToListBtn,
                backgroundColor: isWatched ? '#e50914' : 'rgba(255,255,255,0.1)',
                color: isWatched ? 'white' : '#7a8ba3',
                transform: isHovered ? 'scale(1.1)' : 'scale(1)',
              }}
              title={isWatched ? "Listeden Çıkar" : "Listeme Ekle"}
            >
              {isWatched ? '✓' : '+'}
            </button>
          )}

          <div style={styles.metadata}>
            {year && <span>{year}</span>}
            {year && <span style={{ opacity: 0.3 }}>|</span>}
            <span style={styles.langBadge}>{lang}</span>
          </div>
        </div>
      </Link>
    </div>
  );
}
