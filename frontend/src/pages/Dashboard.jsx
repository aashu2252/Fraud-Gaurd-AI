import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { logAction } from '../services/api';

const PRODUCTS = [
    { product_id: 'PROD_T01', name: 'Urban Flex Tee', product_category: 'Clothing', order_value: 1299, emoji: '👕', gradient: 'linear-gradient(135deg,#1e1b4b,#312e81)', sizes: ['XS', 'S', 'M', 'L', 'XL'] },
    { product_id: 'PROD_T02', name: 'Neo Denim Jacket', product_category: 'Clothing', order_value: 4999, emoji: '🧥', gradient: 'linear-gradient(135deg,#1c1917,#292524)', sizes: ['S', 'M', 'L', 'XL'] },
    { product_id: 'PROD_E01', name: 'Quantum Earbuds Pro', product_category: 'Electronics', order_value: 12999, emoji: '🎧', gradient: 'linear-gradient(135deg,#0c1445,#1e3a5f)' },
    { product_id: 'PROD_E02', name: 'AuraWatch Ultra', product_category: 'Electronics', order_value: 24999, emoji: '⌚', gradient: 'linear-gradient(135deg,#1a1a2e,#16213e)' },
    { product_id: 'PROD_S01', name: 'StridePro Runners', product_category: 'Footwear', order_value: 7499, emoji: '👟', gradient: 'linear-gradient(135deg,#0d1f0d,#1a3a1a)', sizes: ['7', '8', '9', '10', '11'] },
    { product_id: 'PROD_S02', name: 'Cloud-9 Loafers', product_category: 'Footwear', order_value: 5499, emoji: '👞', gradient: 'linear-gradient(135deg,#2d1b00,#4a3000)', sizes: ['7', '8', '9', '10', '11'] },
    { product_id: 'PROD_A01', name: 'Velocity Backpack', product_category: 'Accessories', order_value: 2999, emoji: '🎒', gradient: 'linear-gradient(135deg,#1a0533,#2d0a50)' },
    { product_id: 'PROD_B01', name: 'Deep Work Masterclass', product_category: 'Books', order_value: 499, emoji: '📚', gradient: 'linear-gradient(135deg,#0a1628,#1a2f50)' },
];

const CATEGORIES = ['All', 'Clothing', 'Electronics', 'Footwear', 'Accessories', 'Books'];

const STATS = [
    { label: 'Products', value: '2,400+', icon: '📦' },
    { label: 'Brands', value: '180+', icon: '🏷️' },
    { label: 'Happy Customers', value: '98.2%', icon: '⭐' },
    { label: 'Fraud Prevented', value: '₹4.2Cr', icon: '🛡️' },
];

function ProductCard({ product, onAddToCart }) {
    const [selectedSize, setSelectedSize] = useState('');
    const [added, setAdded] = useState(false);

    const handleAdd = async () => {
        if (product.sizes && !selectedSize) {
            alert('Please select a size first.');
            return;
        }
        const item = { ...product, size_variant: selectedSize || null };
        onAddToCart(item);
        setAdded(true);
        setTimeout(() => setAdded(false), 1800);
    };

    return (
        <div className="product-card">
            <div className="product-card-image" style={{ background: product.gradient }}>
                <span>{product.emoji}</span>
            </div>
            <div className="product-card-body">
                <div className="product-card-category">{product.product_category}</div>
                <div className="product-card-name">{product.name}</div>
                <div className="product-card-price">₹{product.order_value.toLocaleString('en-IN')}</div>
                {product.sizes && (
                    <div className="select-wrapper">
                        <select className="size-select" value={selectedSize} onChange={e => setSelectedSize(e.target.value)}>
                            <option value="">Select Size</option>
                            {product.sizes.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                    </div>
                )}
                <button
                    className={`add-to-cart-btn ${added ? 'added' : ''}`}
                    onClick={handleAdd}
                >
                    {added ? '✓ Added to Cart!' : '+ Add to Cart'}
                </button>
            </div>
        </div>
    );
}

export default function Dashboard({ addToCart, currentUser }) {
    const [activeCategory, setActiveCategory] = useState('All');
    const navigate = useNavigate();

    const filtered = activeCategory === 'All'
        ? PRODUCTS
        : PRODUCTS.filter(p => p.product_category === activeCategory);

    const handleAddToCart = async (product) => {
        addToCart(product);
        // Log action to backend
        try {
            await logAction({
                user_hash: currentUser.hash,
                action_type: 'AddToCart',
                product_id: product.product_id,
                product_category: product.product_category,
                order_value: product.order_value,
                size_variant: product.size_variant || null,
            });
        } catch (e) {
            // Backend offline — still allow demo
        }
    };

    return (
        <div>
            {/* Stats Bar */}
            <div className="stats-bar">
                {STATS.map(s => (
                    <div className="stat-card" key={s.label}>
                        <div className="stat-value">{s.icon} {s.value}</div>
                        <div className="stat-label">{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Page Header */}
            <div className="page-header">
                <h1>Featured Products</h1>
                <p>Premium products with real-time fraud protection on every order</p>
            </div>

            {/* Category Filters */}
            <div className="filter-pills">
                {CATEGORIES.map(cat => (
                    <button
                        key={cat}
                        className={`filter-pill ${activeCategory === cat ? 'active' : ''}`}
                        onClick={() => setActiveCategory(cat)}
                    >
                        {cat}
                    </button>
                ))}
            </div>

            {/* Product Grid */}
            <div className="product-grid">
                {filtered.map(product => (
                    <ProductCard
                        key={product.product_id}
                        product={product}
                        onAddToCart={handleAddToCart}
                    />
                ))}
            </div>

            <div style={{ textAlign: 'center', marginTop: '32px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                🛡️ ReturnGuard AI monitors every transaction in real time. Use the <strong style={{ color: 'var(--accent-violet)' }}>🧪 Simulator</strong> panel (bottom-right) to switch user risk profiles.
            </div>
        </div>
    );
}
