import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRiskScore, logAction } from '../services/api';

function RiskBanner({ riskData, loading }) {
    if (loading) {
        return (
            <div className="risk-banner" style={{ border: '1px solid var(--border)', background: 'var(--bg-card)' }}>
                <div className="loading-spinner">
                    <div className="spinner" />
                    <span>Analyzing behavioral fingerprint...</span>
                </div>
            </div>
        );
    }

    if (!riskData) return null;
    const { risk_score, risk_level, reason_codes, model_used } = riskData;
    const level = risk_level?.toLowerCase();

    const icons = { high: '🚨', medium: '⚠️', low: '✅' };
    const titles = {
        high: 'High Fraud Risk Detected',
        medium: 'Elevated Risk — Enhanced Verification Active',
        low: 'Verified Trusted Shopper',
    };
    const subtitles = {
        high: 'Behavioral analysis flagged this account. Some payment methods are restricted.',
        medium: 'Unusual patterns detected. Manual review may apply.',
        low: 'No suspicious activity detected. All payment options available.',
    };

    return (
        <div className={`risk-banner ${level} ${level === 'high' ? 'pulse' : ''}`}>
            <div className="risk-banner-header">
                <span className="risk-icon">{icons[level]}</span>
                <div>
                    <div className={`risk-title ${level}`}>{titles[level]}</div>
                    <div className="risk-subtitle">{subtitles[level]}</div>
                </div>
                <div className={`risk-score-display ${level}`}>{risk_score}</div>
            </div>
            <div className="risk-gauge">
                <div
                    className={`risk-gauge-fill ${level}`}
                    style={{ width: `${risk_score}%` }}
                />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div className="risk-reasons">
                    {reason_codes?.map(code => (
                        <span key={code} className="reason-tag">{code}</span>
                    ))}
                </div>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                    via {model_used}
                </span>
            </div>
        </div>
    );
}

const PAYMENT_METHODS = [
    { id: 'upi', icon: '🔮', name: 'UPI / PhonePe / GPay', desc: 'Instant payment', requiresLowRisk: false },
    { id: 'card', icon: '💳', name: 'Credit / Debit Card', desc: 'Visa, Mastercard, RuPay', requiresLowRisk: false },
    { id: 'netbanking', icon: '🏦', name: 'Net Banking', desc: 'All major Indian banks', requiresLowRisk: false },
    { id: 'emi', icon: '📅', name: 'EMI (No Cost)', desc: '3, 6, 12 months available', requiresLowRisk: false },
    { id: 'cod', icon: '💵', name: 'Cash on Delivery', desc: 'Pay when delivered', requiresLowRisk: true },
];

export default function Checkout({ cart, removeFromCart, currentUser }) {
    const navigate = useNavigate();
    const [riskData, setRiskData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedPayment, setSelectedPayment] = useState('upi');
    const [ordered, setOrdered] = useState(false);

    const isHighRisk = riskData?.risk_score > 80;

    useEffect(() => {
        if (!currentUser?.hash) return;
        setLoading(true);
        setRiskData(null);

        getRiskScore(currentUser.hash, cart)
            .then(data => setRiskData(data))
            .catch(() => {
                // Backend offline — simulate based on user profile
                const fallback = {
                    low_risk: { risk_score: 12, risk_level: 'LOW', reason_codes: ['no_significant_flags'], model_used: 'demo_mode' },
                    medium_risk: { risk_score: 58, risk_level: 'MEDIUM', reason_codes: ['high_return_ratio'], model_used: 'demo_mode' },
                    high_risk: { risk_score: 91, risk_level: 'HIGH', reason_codes: ['size_variation_detected', 'rapid_return_pattern', 'high_return_ratio'], model_used: 'demo_mode' },
                };
                setRiskData(fallback[currentUser.id] || fallback.low_risk);
            })
            .finally(() => setLoading(false));
    }, [currentUser?.hash]);

    const total = cart.reduce((sum, item) => sum + item.order_value * (item.qty || 1), 0);
    const shipping = total > 0 ? (total > 5000 ? 0 : 99) : 0;
    const grandTotal = total + shipping;

    if (ordered) {
        return (
            <div style={{ textAlign: 'center', padding: '80px 20px' }}>
                <div style={{ fontSize: '4rem', marginBottom: '16px' }}>🎉</div>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '8px' }}>Order Placed!</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Your order has been successfully placed and confirmed.</p>
                <button className="back-btn" style={{ marginTop: '24px' }} onClick={() => { navigate('/'); setOrdered(false); }}>
                    ← Continue Shopping
                </button>
            </div>
        );
    }

    if (cart.length === 0) {
        return (
            <div className="empty-cart">
                <div className="empty-cart-icon">🛒</div>
                <h3>Your cart is empty</h3>
                <p>Add some products and come back to checkout!</p>
                <button className="back-btn" onClick={() => navigate('/')}>← Back to Shop</button>
            </div>
        );
    }

    return (
        <div>
            <div className="page-header">
                <h1>Checkout</h1>
                <p>Complete your order — fraud risk is assessed automatically</p>
            </div>

            {/* Risk Banner — THE CORE FEATURE */}
            <RiskBanner riskData={riskData} loading={loading} />

            <div className="checkout-layout">
                {/* Cart Items */}
                <div>
                    <div className="checkout-title">🛒 Your Cart ({cart.length} items)</div>
                    {cart.map((item, idx) => (
                        <div className="cart-item" key={idx}>
                            <span className="cart-item-emoji" style={{ fontSize: '1.8rem' }}>
                                {['👕', '🧥', '🎧', '⌚', '👟', '👞', '🎒', '📚'][['PROD_T01', 'PROD_T02', 'PROD_E01', 'PROD_E02', 'PROD_S01', 'PROD_S02', 'PROD_A01', 'PROD_B01'].indexOf(item.product_id)] || '📦'}
                            </span>
                            <div className="cart-item-info">
                                <div className="cart-item-name">{item.name}</div>
                                <div className="cart-item-meta">
                                    {item.product_category}
                                    {item.size_variant && ` · Size: ${item.size_variant}`}
                                    {item.qty > 1 && ` · Qty: ${item.qty}`}
                                </div>
                            </div>
                            <div className="cart-item-price">₹{(item.order_value * (item.qty || 1)).toLocaleString('en-IN')}</div>
                            <button className="cart-item-remove" onClick={() => removeFromCart(idx)} title="Remove">✕</button>
                        </div>
                    ))}
                </div>

                {/* Order Summary */}
                <div>
                    <div className="glass-card" style={{ padding: '24px' }}>
                        <div className="summary-title">📋 Order Summary</div>

                        <div className="summary-row">
                            <span style={{ color: 'var(--text-secondary)' }}>Subtotal</span>
                            <span>₹{total.toLocaleString('en-IN')}</span>
                        </div>
                        <div className="summary-row">
                            <span style={{ color: 'var(--text-secondary)' }}>Shipping</span>
                            <span style={{ color: shipping === 0 ? 'var(--accent-green)' : 'inherited' }}>
                                {shipping === 0 ? 'FREE' : `₹${shipping}`}
                            </span>
                        </div>
                        {isHighRisk && (
                            <div className="summary-row">
                                <span style={{ color: 'var(--accent-amber)', fontSize: '0.8rem' }}>🚨 Risk Surcharge</span>
                                <span style={{ color: 'var(--accent-amber)', fontSize: '0.8rem' }}>₹0</span>
                            </div>
                        )}
                        <div className="summary-row total">
                            <span>Total</span>
                            <span className="amount">₹{grandTotal.toLocaleString('en-IN')}</span>
                        </div>

                        {/* Payment Methods */}
                        <div className="payment-section">
                            <div className="payment-title">💳 Payment Method</div>

                            {/* HIGH RISK WARNING */}
                            {isHighRisk && (
                                <div style={{
                                    background: 'rgba(239,68,68,0.08)',
                                    border: '1px solid rgba(239,68,68,0.25)',
                                    borderRadius: 'var(--radius-sm)',
                                    padding: '10px 12px',
                                    marginBottom: '12px',
                                    fontSize: '0.8rem',
                                    color: 'var(--accent-red)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                }}>
                                    🚫 <strong>Cash on Delivery is currently unavailable for this order.</strong>
                                </div>
                            )}

                            {PAYMENT_METHODS.map(method => {
                                const blocked = method.requiresLowRisk && isHighRisk;
                                const isSelected = selectedPayment === method.id && !blocked;
                                return (
                                    <button
                                        key={method.id}
                                        className={`payment-method ${isSelected ? 'selected' : ''} ${blocked ? 'disabled' : ''}`}
                                        onClick={() => !blocked && setSelectedPayment(method.id)}
                                        disabled={blocked}
                                    >
                                        <span className="payment-icon">{method.icon}</span>
                                        <div>
                                            <div className="payment-name">{method.name}</div>
                                            <div className="payment-desc">{method.desc}</div>
                                        </div>
                                        {blocked && <span className="cod-blocked-badge">Blocked</span>}
                                        {isSelected && !blocked && (
                                            <span style={{ marginLeft: 'auto', color: 'var(--accent-green)', fontWeight: 700 }}>✓</span>
                                        )}
                                    </button>
                                );
                            })}
                        </div>

                        <button
                            className="place-order-btn"
                            onClick={() => setOrdered(true)}
                        >
                            Place Order · ₹{grandTotal.toLocaleString('en-IN')} →
                        </button>
                    </div>

                    {/* Risk Score Context */}
                    {riskData && !loading && (
                        <div style={{ marginTop: '12px', padding: '12px 16px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            🛡️ Risk Score: <strong style={{ color: 'var(--text-secondary)' }}>{riskData.risk_score}/100</strong> ·
                            Model: <strong style={{ color: 'var(--text-secondary)' }}>{riskData.model_used}</strong> ·
                            Powered by ReturnGuard AI
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
