'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';

const styles = {
    container: {
        position: 'fixed' as const,
        bottom: '2rem',
        right: '2rem',
        zIndex: 1000,
    },
    fab: {
        width: '65px',
        height: '65px',
        borderRadius: '50%',
        background: 'rgba(26, 34, 53, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(229, 9, 20, 0.5)',
        boxShadow: '0 8px 32px rgba(229, 9, 20, 0.3)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        animation: 'fabPulse 2s infinite',
    },
    chatWindow: {
        position: 'absolute' as const,
        bottom: '80px',
        right: '0',
        width: '400px',
        height: '600px',
        backgroundColor: '#1a2235',
        borderRadius: '1.5rem',
        boxShadow: '0 20px 60px rgba(0,0,0,0.6)',
        border: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column' as const,
        overflow: 'hidden',
        animation: 'slideIn 0.3s ease-out',
    },
    header: {
        position: 'absolute' as const,
        top: 0,
        left: 0,
        right: 0,
        padding: '1rem 1.5rem',
        background: 'rgba(26, 34, 53, 0.6)',
        backdropFilter: 'blur(1px)',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        zIndex: 10,
    },
    messages: {
        flex: 1,
        padding: '5rem 1.5rem 1.5rem 1.5rem',
        overflowY: 'auto' as const,
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '1rem',
    },
    message: {
        maxWidth: '85%',
        padding: '0.8rem 1.2rem',
        borderRadius: '1rem',
        fontSize: '0.95rem',
        lineHeight: 1.5,
        whiteSpace: 'pre-wrap' as const,
    },
    userMessage: {
        alignSelf: 'flex-end',
        backgroundColor: '#e50914',
        color: 'white',
        borderBottomRightRadius: '0.2rem',
    },
    aiMessage: {
        alignSelf: 'flex-start',
        backgroundColor: 'rgba(255,255,255,0.05)',
        color: '#e0e0e0',
        borderBottomLeftRadius: '0.2rem',
    },
    inputArea: {
        padding: '1.25rem',
        borderTop: '1px solid rgba(255,255,255,0.05)',
        display: 'flex',
        gap: '0.75rem',
    },
    input: {
        flex: 1,
        background: 'rgba(0,0,0,0.2)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '0.75rem',
        padding: '0.75rem 1rem',
        color: 'white',
        outline: 'none',
    },
    sendBtn: {
        background: '#e50914',
        color: 'white',
        border: 'none',
        borderRadius: '0.75rem',
        padding: '0 1.25rem',
        cursor: 'pointer',
        fontWeight: 700,
    },
    quickReplies: {
        padding: '0 1.5rem 1rem 1.5rem',
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '0.5rem',
    },
    replyBtn: {
        background: 'rgba(255, 255, 255, 0.03)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        color: '#b8c5d6',
        padding: '0.5rem 1rem',
        borderRadius: '2rem',
        fontSize: '0.8rem',
        textAlign: 'left' as const,
        cursor: 'pointer',
        transition: '0.2s',
    },
    skeleton: {
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '0.5rem',
        height: '1rem',
        marginBottom: '0.5rem',
        animation: 'pulse 1.5s infinite ease-in-out',
    }
};

interface Message {
    text: string;
    sender: 'user' | 'ai';
}

export default function ChatBot() {
    const [isOpen, setIsOpen] = useState(false);
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { text: "Merhaba! Ben CineMatch asistanı. Size nasıl yardımcı olabilirim?", sender: 'ai' }
    ]);
    const [loading, setLoading] = useState(false);
    const [userId, setUserId] = useState<number | undefined>(undefined);
    const [showPrompts, setShowPrompts] = useState(true);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const checkUser = () => {
            const savedUser = localStorage.getItem('currentUser');
            if (savedUser) {
                setUserId(JSON.parse(savedUser).user_id);
            } else {
                setUserId(undefined);
            }
        };
        checkUser();
        // Auth state changes
        const interval = setInterval(checkUser, 2000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isOpen]);

    const handleSend = async (text: string) => {
        const msg = text || input;
        if (!msg.trim() || loading) return;

        const userMsg: Message = { text: msg, sender: 'user' };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);
        setShowPrompts(false); // Hide prompts after use

        try {
            const response = await sendChatMessage(msg, userId);
            setMessages(prev => [...prev, { text: response, sender: 'ai' }]);
        } catch (err: any) {
            const errorMessage = err.message || "Bilinmeyen bir hata oluştu.";
            setMessages(prev => [...prev, { text: `⚠️ Hata: ${errorMessage}`, sender: 'ai' }]);
        } finally {
            setLoading(false);
        }
    };

    const quickReplies = [
        "Bugün ne izlemeliyim?",
        "Korku filmi önerir misin?",
        "En popüler filmler hangileri?"
    ];

    const formatMessage = (text: string) => {
        const parts = text.split(/(\*\*.*?\*\*)/g);
        return parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={i} style={{ color: '#ffffff', fontWeight: 800 }}>{part.slice(2, -2)}</strong>;
            }
            return part;
        });
    };

    return (
        <div style={styles.container}>
            <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(20px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes pulse {
          0% { opacity: 0.3; transform: scale(0.98); }
          50% { opacity: 0.6; transform: scale(1); }
          100% { opacity: 0.3; transform: scale(0.98); }
        }
        @keyframes fabPulse {
          0% { box-shadow: 0 0 0 0 rgba(229, 9, 20, 0.4); }
          70% { box-shadow: 0 0 0 15px rgba(229, 9, 20, 0); }
          100% { box-shadow: 0 0 0 0 rgba(229, 9, 20, 0); }
        }
      `}</style>

            {isOpen && (
                <div style={styles.chatWindow}>
                    <div style={styles.header}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4Z" fill="#e50914" opacity="0.4" />
                                <path d="M7 11C7 9.89543 7.89543 9 9 9H15C16.1046 9 17 9.89543 17 11V15C17 16.1046 16.1046 17 15 17H9C7.89543 17 7 16.1046 7 15V11Z" fill="#e50914" />
                                <circle cx="10" cy="13" r="1" fill="white" />
                                <circle cx="14" cy="13" r="1" fill="white" />
                                <path d="M9 7L10 9M15 7L14 9" stroke="#e50914" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                            <div>
                                <div style={{ fontWeight: 800, fontSize: '0.9rem' }}>CineMatch AI</div>
                                <div style={{ fontSize: '0.7rem', color: '#00ff00', fontWeight: 600 }}>Çevrimiçi</div>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: '#7a8ba3', cursor: 'pointer', fontSize: '1.2rem' }}>✕</button>
                    </div>

                    <div style={styles.messages} ref={scrollRef}>
                        {messages.map((m, i) => (
                            <div key={i} style={{ ...styles.message, ...(m.sender === 'user' ? styles.userMessage : styles.aiMessage) }}>
                                {formatMessage(m.text)}
                            </div>
                        ))}
                        {loading && (
                            <div style={{ ...styles.message, ...styles.aiMessage, width: '70%' }}>
                                <div style={{ ...styles.skeleton, width: '100%', animationDelay: '0s' }} />
                                <div style={{ ...styles.skeleton, width: '85%', animationDelay: '0.2s' }} />
                                <div style={{ ...styles.skeleton, width: '60%', animationDelay: '0.4s' }} />
                            </div>
                        )}

                        {!userId && !loading && (
                            <div style={{ ...styles.aiMessage, ...styles.message, backgroundColor: 'rgba(229,9,20,0.1)', border: '1px solid rgba(229,9,20,0.3)', marginTop: '1rem', width: '100%' }}>
                                🔓 <strong>Kişiselleştirilmiş öneriler için giriş yapmalısınız.</strong>
                                <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>Chatbot, film zevkinizi analiz etmek için üye kaydınıza ihtiyaç duyar.</p>
                                <button
                                    onClick={() => window.dispatchEvent(new CustomEvent('open-auth'))}
                                    style={{ background: '#e50914', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.5rem', marginTop: '0.75rem', cursor: 'pointer', fontWeight: 700 }}
                                >
                                    Giriş Yap / Kayıt Ol
                                </button>
                            </div>
                        )}
                    </div>

                    {showPrompts && (
                        <div style={styles.quickReplies}>
                            {quickReplies.map((r, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleSend(r)}
                                    style={{ ...styles.replyBtn, opacity: userId ? 1 : 0.4 }}
                                    disabled={!userId}
                                    className="hb-reply"
                                >
                                    {r}
                                </button>
                            ))}
                        </div>
                    )}

                    <form onSubmit={(e) => { e.preventDefault(); handleSend(input); }} style={styles.inputArea}>
                        <input
                            style={{ ...styles.input, opacity: userId ? 1 : 0.5 }}
                            placeholder={userId ? "Mesajınızı yazın..." : "Sohbet için giriş yapın"}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={loading || !userId}
                        />
                        <button type="submit" style={styles.sendBtn} disabled={loading || !userId}>Gönder</button>
                    </form>
                </div>
            )}

            <button
                onClick={() => setIsOpen(!isOpen)}
                style={styles.fab}
                onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'scale(1.1) rotate(5deg)';
                    e.currentTarget.style.boxShadow = '0 12px 40px rgba(229, 9, 20, 0.5)';
                    e.currentTarget.style.borderColor = 'rgba(229, 9, 20, 0.8)';
                }}
                onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'scale(1) rotate(0deg)';
                    e.currentTarget.style.boxShadow = '0 8px 32px rgba(229, 9, 20, 0.3)';
                    e.currentTarget.style.borderColor = 'rgba(229, 9, 20, 0.5)';
                }}
            >
                {isOpen ? '✕' : (
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4Z" fill="#e50914" opacity="0.4" />
                        <path d="M7 11C7 9.89543 7.89543 9 9 9H15C16.1046 9 17 9.89543 17 11V15C17 16.1046 16.1046 17 15 17H9C7.89543 17 7 16.1046 7 15V11Z" fill="#e50914" />
                        <circle cx="10" cy="13" r="1" fill="white" />
                        <circle cx="14" cy="13" r="1" fill="white" />
                        <path d="M9 7L10 9M15 7L14 9" stroke="#e50914" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                )}
            </button>
        </div>
    );
}
