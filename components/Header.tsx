'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

const styles = {
  header: {
    background: 'rgba(10, 14, 26, 0.95)',
    backdropFilter: 'blur(10px)',
    borderBottom: '1px solid #2a3548',
    position: 'sticky' as const,
    top: 0,
    zIndex: 100,
    padding: '1rem 0',
  },
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '0 1.5rem',
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    fontSize: '1.75rem',
    fontWeight: 800,
    cursor: 'pointer',
    transition: 'transform 0.2s ease',
  },
  logoIcon: {
    fontSize: '2rem',
  },
  logoText: {
    background: 'linear-gradient(135deg, #e50914, #ff6b6b)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    letterSpacing: '-0.5px',
  },
  nav: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.5rem',
  },
  navLink: {
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    fontWeight: 500,
    transition: 'all 0.2s ease',
    color: '#ffffff',
    textDecoration: 'none',
    cursor: 'pointer',
  },
  profileBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.5rem 1.25rem',
    borderRadius: '2rem',
    backgroundColor: 'rgba(229, 9, 20, 0.1)',
    border: '1px solid rgba(229, 9, 20, 0.3)',
    color: '#e50914',
    fontWeight: 700,
    cursor: 'pointer',
    transition: '0.3s',
  },
  logoutBtn: {
    background: 'none',
    border: 'none',
    color: '#ff6b6b',
    fontSize: '0.8rem',
    fontWeight: 600,
    cursor: 'pointer',
    padding: '0.25rem 0.5rem',
    marginTop: '0.25rem',
    textAlign: 'right' as const,
    opacity: 0.8,
    transition: '0.3s',
  },
  dropdown: {
    position: 'absolute' as const,
    top: '110%',
    right: 0,
    background: 'rgba(26, 34, 53, 0.95)',
    backdropFilter: 'blur(20px)',
    border: '1px solid #2a3548',
    borderRadius: '1rem',
    minWidth: '200px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
    padding: '0.5rem',
    zIndex: 110,
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.25rem',
  },
  dropdownItem: {
    padding: '1rem',
    borderRadius: '0.5rem',
    color: 'white',
    fontSize: '0.95rem',
    fontWeight: 500,
    cursor: 'pointer',
    transition: '0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    border: 'none',
    background: 'none',
    width: '100%',
    textAlign: 'left' as const,
  },
  modalOverlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    backgroundColor: 'rgba(0,0,0,0.85)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1001,
  },
  modalCard: {
    background: '#1a2235',
    padding: '2.5rem',
    borderRadius: '1.5rem',
    width: '90%',
    maxWidth: '400px',
    textAlign: 'center' as const,
    border: '1px solid rgba(255,255,255,0.1)',
    boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
  },
  modalBtn: {
    padding: '0.8rem 1.5rem',
    borderRadius: '0.75rem',
    border: 'none',
    fontWeight: 700,
    cursor: 'pointer',
    transition: '0.3s',
    flex: 1,
  }
};

export default function Header() {
  const [user, setUser] = useState<any>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  useEffect(() => {
    const checkUser = () => {
      const savedUser = localStorage.getItem('currentUser');
      if (savedUser) setUser(JSON.parse(savedUser));
      else setUser(null);
    };

    checkUser();
    window.addEventListener('storage', checkUser);
    const interval = setInterval(checkUser, 1000);
    return () => {
      window.removeEventListener('storage', checkUser);
      clearInterval(interval);
    };
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    if (!showDropdown) return;
    const close = () => setShowDropdown(false);
    window.addEventListener('click', close);
    return () => window.removeEventListener('click', close);
  }, [showDropdown]);

  const triggerAuth = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.dispatchEvent(new CustomEvent('open-auth'));
  };

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    setUser(null);
    window.location.reload();
  };

  return (
    <header style={styles.header}>
      <div style={styles.container}>
        <div style={styles.headerContent}>
          <div
            onClick={() => window.dispatchEvent(new CustomEvent('reset-selection'))}
            style={{ textDecoration: 'none', cursor: 'pointer' }}
          >
            <h1 style={styles.logo}>
              <span style={styles.logoIcon}>🎬</span>
              <span style={styles.logoText}>CineMatch</span>
            </h1>
          </div>

          <nav style={styles.nav}>
            <div style={{ position: 'relative' }}>
              <div
                style={styles.profileBtn}
                onClick={(e) => {
                  e.stopPropagation();
                  if (user) setShowDropdown(!showDropdown);
                  else triggerAuth(e);
                }}
              >
                <span>{user ? user.full_name : 'Giriş Yap / Kayıt Ol'}</span>
                {user && <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>{showDropdown ? '▲' : '▼'}</span>}
              </div>

              {showDropdown && user && (
                <div style={styles.dropdown} onClick={(e) => e.stopPropagation()}>
                  <div style={{ padding: '0.5rem 1rem', borderBottom: '1px solid #2a3548', marginBottom: '0.25rem' }}>
                    <p style={{ color: '#7a8ba3', fontSize: '0.8rem', margin: 0 }}>Hesabım</p>
                    <p style={{ color: 'white', fontWeight: 600, fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.email}</p>
                  </div>
                  <button
                    style={{ ...styles.dropdownItem, color: '#ff6b6b' }}
                    onClick={() => { setShowDropdown(false); setShowLogoutConfirm(true); }}
                  >Çıkış Yap
                  </button>
                </div>
              )}
            </div>
          </nav>
        </div>
      </div>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div style={styles.modalOverlay} onClick={() => setShowLogoutConfirm(false)}>
          <div style={styles.modalCard} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👋</div>
            <h2 style={{ color: 'white', marginBottom: '0.5rem', fontSize: '1.5rem' }}>Gidiyor musunuz?</h2>
            <p style={{ color: '#7a8ba3', marginBottom: '2rem' }}>Çıkış yapmak istediğinize emin misiniz? Sizi buralarda görmeyi özleyeceğiz.</p>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                style={{ ...styles.modalBtn, background: '#2a3548', color: 'white' }}
                onClick={() => setShowLogoutConfirm(false)}
              >
                Vazgeç
              </button>
              <button
                style={{ ...styles.modalBtn, background: 'linear-gradient(135deg, #e50914, #ff6b6b)', color: 'white' }}
                onClick={handleLogout}
              >
                Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
