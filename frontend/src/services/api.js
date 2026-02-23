import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

/**
 * Get real-time fraud risk score for a user + cart.
 * @param {string} userHash - Salted SHA-256 hash of user identity
 * @param {Array} cart - Array of cart items
 * @returns {Promise<{risk_score, risk_level, reason_codes, features_used, model_used}>}
 */
export async function getRiskScore(userHash, cart = []) {
  const { data } = await api.post('/v1/get-risk-score', {
    user_hash: userHash,
    cart: cart.map(item => ({
      product_id: item.product_id,
      category: item.product_category,
      size: item.size_variant || null,
      value: item.order_value,
    })),
  });
  return data;
}

/**
 * Log a behavioral action to the backend.
 */
export async function logAction(payload) {
  const { data } = await api.post('/v1/log-action', payload);
  return data;
}

/**
 * Get transaction history for a user.
 */
export async function getHistory(userHash) {
  const { data } = await api.get(`/v1/history/${userHash}`);
  return data;
}

/**
 * Get score history for a user.
 */
export async function getScoreHistory(userHash) {
  const { data } = await api.get(`/v1/score-history/${userHash}`);
  return data;
}

export default api;
