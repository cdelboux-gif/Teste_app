import * as SecureStore from 'expo-secure-store';

import { apiRequest } from './api';

const ACCESS_TOKEN_KEY = 'vitapoint_access_token';
const REFRESH_TOKEN_KEY = 'vitapoint_refresh_token';

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

async function saveTokens(tokens: TokenPair) {
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokens.access_token);
  await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export async function login(email: string, password: string) {
  const tokens = await apiRequest<TokenPair>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  await saveTokens(tokens);
  return tokens;
}

export async function register(email: string, password: string) {
  const tokens = await apiRequest<TokenPair>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  await saveTokens(tokens);
  return tokens;
}

export async function getAccessToken() {
  return SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
}

export async function logout() {
  await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
  await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
}
