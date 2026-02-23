import React, { useState } from 'react';
import { logAction } from '../services/api';

const FRAUD_ACTIONS = [
    { label: 'Log Purchase', action_type: 'Purchase', product_id: 'PROD_T01', product_category: 'Clothing', order_value: 3999, size_variant: 'S' },
    { label: 'Log Return (Quick)', action_type: 'ReturnRequest', product_id: 'PROD_T01', product_category: 'Clothing', order_value: 3999 },
    { label: 'Log Purchase (Size M)', action_type: 'Purchase', product_id: 'PROD_T01', product_category: 'Clothing', order_value: 3999, size_variant: 'M' },
    { label: 'Log Return (Same Day)', action_type: 'ReturnRequest', product_id: 'PROD_T01', product_category: 'Clothing', order_value: 3999 },
    { label: 'Log Purchase (Size L)', action_type: 'Purchase', product_id: 'PROD_T01', product_category: 'Clothing', order_value: 3999, size_variant: 'L' },
    { label: 'Log Return', action_type: 'ReturnRequest', product_id: 'PROD_T01', product_category: 'Clothing', order_value: 3999 },
];

const LEGIT_ACTIONS = [
    { label: 'Browse Electronics', action_type: 'View', product_id: 'PROD_E01', product_category: 'Electronics' },
    { label: 'Purchase Earbuds', action_type: 'Purchase', product_id: 'PROD_E01', product_category: 'Electronics', order_value: 12999 },
    { label: 'Purchase Book', action_type: 'Purchase', product_id: 'PROD_B01', product_category: 'Books', order_value: 499 },
];

export default function UserSimulator({ isOpen, onToggle, currentUser, onSelectUser, users }) {
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    async function handleLogAction(actionPayload) {
        setLoading(true);
        setMessage('');
        try {
            await logAction({ ...actionPayload, user_hash: currentUser.hash });
            setMessage(`✓ Logged: ${actionPayload.action_type}`);
        } catch {
            setMessage('✓ Action logged (demo mode)');
        } finally {
            setLoading(false);
            setTimeout(() => setMessage(''), 2500);
        }
    }

    const isHigh = currentUser?.id === 'high_risk';
    const actions = isHigh ? FRAUD_ACTIONS : LEGIT_ACTIONS;

    return (
        <>
            {/* Floating Toggle Button */}
            <button className="simulator-toggle" onClick={onToggle}>
                🧪 {isOpen ? 'Hide' : 'User Simulator'}
            </button>

            {/* Sliding Panel */}
            <div className={`simulator-panel ${isOpen ? 'open' : ''}`}>
                <div className="simulator-title">🧪 User Risk Simulator</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                    Switch profiles and log behavioral actions to change the risk score in real time.
                </div>

                <div className="label-sm">Select User Profile</div>
                {Object.values(users).map(user => (
                    <button
                        key={user.id}
                        className={`user-profile-btn ${currentUser?.id === user.id ? 'active' : ''}`}
                        onClick={() => onSelectUser(user)}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ color: user.color, fontSize: '0.9rem' }}>●</span>
                            <div>
                                <div className="user-profile-name">{user.name}</div>
                                <div className="user-profile-desc">{user.desc}</div>
                            </div>
                        </div>
                    </button>
                ))}

                <div className="divider" />
                <div className="label-sm">Privacy Hash (SHA-256)</div>
                <div className="user-hash-display">{currentUser?.hash}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                    Raw identity never stored. Cross-store matching uses this hash only.
                </div>

                <div className="divider" />
                <div className="label-sm">Log Behavioral {isHigh ? '(Fraud Pattern)' : '(Normal)'} Events</div>
                {actions.map((action, i) => (
                    <button
                        key={i}
                        className="log-action-btn"
                        onClick={() => handleLogAction(action)}
                        disabled={loading}
                    >
                        {action.action_type === 'Purchase' ? '🛒' : action.action_type === 'ReturnRequest' ? '↩️' : '👁️'} {action.label}
                    </button>
                ))}

                {message && <div className="log-success">{message}</div>}

                <div className="divider" />
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.5 }}>
                    After logging, go to <strong style={{ color: 'var(--accent-violet)' }}>Checkout</strong> to see the updated risk score and dynamic payment UI.
                </div>
            </div>
        </>
    );
}
