import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Checkout from './pages/Checkout';
import UserSimulator from './components/UserSimulator';
import './index.css';

// Pre-defined demo user hashes
export const DEMO_USERS = {
    low_risk: {
        id: 'low_risk',
        name: 'Priya Sharma (Low Risk)',
        hash: 'a3f4e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4',
        desc: 'Normal shopper, rare returns',
        color: '#10b981',
    },
    medium_risk: {
        id: 'medium_risk',
        name: 'Rahul Verma (Medium Risk)',
        hash: 'b4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4',
        desc: 'Occasional returns, occasional issues',
        color: '#f59e0b',
    },
    high_risk: {
        id: 'high_risk',
        name: 'Serial Fraudster (High Risk)',
        hash: 'd6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6',
        desc: 'Wardrobing pattern detected',
        color: '#ef4444',
    },
};

function Navbar({ cartCount, currentUser, onOpenSimulator }) {
    const navigate = useNavigate();
    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <div className="brand-icon">🛡️</div>
                <div className="brand-text">Return<span>Guard</span> AI</div>
            </div>
            <div className="navbar-nav">
                <NavLink to="/" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                    🏪 Shop
                </NavLink>
                <NavLink to="/checkout" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                    🧾 Checkout
                </NavLink>
            </div>
            <div className="navbar-right">
                {currentUser && (
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                        <span style={{ color: currentUser.color }}>●</span> {currentUser.name.split(' (')[0]}
                    </span>
                )}
                <button className="cart-btn" onClick={() => navigate('/checkout')}>
                    🛒 Cart
                    {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
                </button>
            </div>
        </nav>
    );
}

function App() {
    const [cart, setCart] = useState([]);
    const [currentUser, setCurrentUser] = useState(DEMO_USERS.low_risk);
    const [simulatorOpen, setSimulatorOpen] = useState(false);

    const addToCart = (product) => {
        setCart(prev => {
            const existing = prev.find(i => i.product_id === product.product_id && i.size_variant === product.size_variant);
            if (existing) return prev.map(i => i === existing ? { ...i, qty: (i.qty || 1) + 1 } : i);
            return [...prev, { ...product, qty: 1 }];
        });
    };

    const removeFromCart = (idx) => {
        setCart(prev => prev.filter((_, i) => i !== idx));
    };

    return (
        <BrowserRouter>
            <div className="app-layout">
                <Navbar cartCount={cart.length} currentUser={currentUser} />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard addToCart={addToCart} currentUser={currentUser} />} />
                        <Route path="/checkout" element={
                            <Checkout cart={cart} removeFromCart={removeFromCart} currentUser={currentUser} />
                        } />
                    </Routes>
                </main>
                <UserSimulator
                    isOpen={simulatorOpen}
                    onToggle={() => setSimulatorOpen(o => !o)}
                    currentUser={currentUser}
                    onSelectUser={setCurrentUser}
                    users={DEMO_USERS}
                />
            </div>
        </BrowserRouter>
    );
}

export default App;
