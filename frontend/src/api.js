import axios from 'axios';

// Configure base URL - update for production
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Query the LLM API with user input
 * @param {string} query - User's question
 * @param {string} userId - User ID for ACL filtering
 * @param {string} token - JWT authentication token
 * @param {object} filters - Optional metadata filters
 * @returns {Promise} Response data
 */
export const queryAPI = async (query, userId, token, filters = null) => {
  try {
    const response = await api.post(
      '/query',
      {
        query,
        user_id: userId,
        filters,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || 'Server error occurred');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Error in request setup
      throw new Error('Error making request: ' + error.message);
    }
  }
};

/**
 * Login and get authentication token
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise} Authentication data
 */
export const login = async (username, password) => {
  try {
    const response = await api.post('/auth/login', {
      username,
      password,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Login failed');
    } else {
      throw new Error('Unable to connect to server');
    }
  }
};

/**
 * Check API health status
 * @returns {Promise} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('API health check failed');
  }
};

export default api;
