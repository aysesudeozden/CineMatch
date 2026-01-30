'use client';

import { useEffect, useState } from 'react';
import { getUsers, User } from '@/lib/api';

const styles = {
  page: {
    minHeight: '100vh',
    padding: '3rem 0',
  },
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '0 1.5rem',
  },
  title: {
    fontSize: '3rem',
    fontWeight: 800,
    textAlign: 'center' as const,
    marginBottom: '3rem',
    background: 'linear-gradient(135deg, #e50914, #ff6b6b)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  error: {
    background: 'rgba(229, 9, 20, 0.1)',
    border: '1px solid #e50914',
    borderRadius: '1rem',
    padding: '1.5rem',
    marginBottom: '2rem',
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    color: '#ff6b6b',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1.5rem',
  },
  skeleton: {
    height: '150px',
    borderRadius: '1rem',
    background: 'linear-gradient(90deg, #1a2235 0%, #242d45 50%, #1a2235 100%)',
    backgroundSize: '1000px 100%',
    animation: 'shimmer 2s infinite',
  },
  card: {
    background: '#1a2235',
    border: '1px solid #2a3548',
    borderRadius: '1rem',
    padding: '2rem',
    display: 'flex',
    alignItems: 'center',
    gap: '1.5rem',
    transition: 'all 0.3s ease',
  },
  avatar: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #e50914, #ff6b6b)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '2rem',
    fontWeight: 700,
    color: 'white',
    flexShrink: 0,
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: '1.25rem',
    fontWeight: 700,
    marginBottom: '0.5rem',
    color: '#ffffff',
  },
  email: {
    color: '#b8c5d6',
    marginBottom: '0.25rem',
  },
  id: {
    color: '#7a8ba3',
    fontSize: '0.875rem',
  },
};

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await getUsers();
      setUsers(data);
    } catch (err) {
      setError('Kullanıcılar yüklenirken bir hata oluştu.');
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={styles.page}>
      <style>{`
        @keyframes shimmer {
          0% { background-position: -1000px 0; }
          100% { background-position: 1000px 0; }
        }
      `}</style>
      <div style={styles.container}>
        <h1 style={styles.title}>Kullanıcılar</h1>

        {error && (
          <div style={styles.error}>
            <span style={{ fontSize: '1.5rem' }}>⚠️</span>
            <p>{error}</p>
          </div>
        )}

        {loading ? (
          <div style={styles.grid}>
            {[...Array(6)].map((_, i) => (
              <div key={i} style={styles.skeleton} />
            ))}
          </div>
        ) : (
          <div style={styles.grid}>
            {users.map((user) => (
              <div key={user.user_id} style={styles.card}>
                <div style={styles.avatar}>
                  {user.full_name.charAt(0).toUpperCase()}
                </div>
                <div style={styles.info}>
                  <h3 style={styles.name}>{user.full_name}</h3>
                  <p style={styles.email}>{user.email}</p>
                  <p style={styles.id}>ID: {user.user_id}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
