import { createContext, useContext, useState, useCallback } from "react";
import * as api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => api.getCurrentUserFromStorage());

  const loginUser = useCallback(async (username, password) => {
    const data = await api.login(username, password);
    setUser({
      role: data.role,
      full_name: data.full_name,
      username: data.username,
    });
    return data;
  }, []);

  const logoutUser = useCallback(() => {
    api.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
