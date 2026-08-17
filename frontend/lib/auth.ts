export function setToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("authToken", token);
  }
}

export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("authToken");
  }
  return null;
}

export function removeToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("authToken");
  }
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

function decodeBase64Url(input: string): string {
  const base64 = input.replace(/-/g, "+").replace(/_/g, "/");
  const pad = base64.length % 4 === 0 ? "" : "=".repeat(4 - (base64.length % 4));
  const binary = atob(base64 + pad);
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
}

export function getUserIdFromToken(): string | null {
  const token = getToken();
  if (!token) return null;
  try {
    const payloadPart = token.split(".")[1];
    if (!payloadPart) return null;
    const payloadJson = decodeBase64Url(payloadPart);
    const payload = JSON.parse(payloadJson) as { user_id?: string };
    return payload.user_id ?? null;
  } catch {
    return null;
  }
}
