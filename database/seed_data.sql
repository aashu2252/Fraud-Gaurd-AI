-- Seed data for demo/testing
-- Uses salted hashes of fictional identities

-- Low-risk user: normal shopping pattern
INSERT INTO users (user_hash, store_id, risk_tier) VALUES
('a3f4e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4', 'STORE_A', 'LOW'),
('b4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4', 'STORE_A', 'LOW'),
('c5f6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2a3b4c5', 'STORE_B', 'MEDIUM'),
('d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'STORE_A', 'HIGH');

-- Low-risk user transactions (normal behavior)
INSERT INTO transactions (user_hash, action_type, timestamp, order_value, product_category, product_id, size_variant, delivery_date, return_date, order_id) VALUES
('a3f4e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4', 'View', NOW() - INTERVAL '30 days', NULL, 'Electronics', 'PROD_001', NULL, NULL, NULL, NULL),
('a3f4e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4', 'Purchase', NOW() - INTERVAL '28 days', 15999.00, 'Electronics', 'PROD_001', NULL, NOW() - INTERVAL '25 days', NULL, 'ORD_001'),
('a3f4e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4', 'Purchase', NOW() - INTERVAL '15 days', 2499.00, 'Books', 'PROD_010', NULL, NOW() - INTERVAL '12 days', NULL, 'ORD_002');

-- High-risk user transactions (wardrobing + high return rate)
INSERT INTO transactions (user_hash, action_type, timestamp, order_value, product_category, product_id, size_variant, delivery_date, return_date, order_id) VALUES
('d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'Purchase', NOW() - INTERVAL '60 days', 3999.00, 'Clothing', 'PROD_T01', 'S', NOW() - INTERVAL '57 days', NOW() - INTERVAL '55 days', 'ORD_H01'),
('d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'ReturnRequest', NOW() - INTERVAL '55 days', 3999.00, 'Clothing', 'PROD_T01', 'S', NULL, NOW() - INTERVAL '55 days', 'ORD_H01'),
('d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'Purchase', NOW() - INTERVAL '45 days', 3999.00, 'Clothing', 'PROD_T01', 'M', NOW() - INTERVAL '42 days', NOW() - INTERVAL '40 days', 'ORD_H02'),
('d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'ReturnRequest', NOW() - INTERVAL '40 days', 3999.00, 'Clothing', 'PROD_T01', 'M', NULL, NOW() - INTERVAL '40 days', 'ORD_H02'),
('d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'Purchase', NOW() - INTERVAL '20 days', 3999.00, 'Clothing', 'PROD_T01', 'L', NOW() - INTERVAL '17 days', NOW() - INTERVAL '15 days', 'ORD_H03'),
('d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'ReturnRequest', NOW() - INTERVAL '15 days', 3999.00, 'Clothing', 'PROD_T01', 'L', NULL, NOW() - INTERVAL '15 days', 'ORD_H03');
