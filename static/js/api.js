function getCookie(name) {
    const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
    return match ? match[2] : null;
}

export async function apiFetch(url, options = {}) {
    const headers = new Headers(options.headers || {});
    const method = (options.method || "GET").toUpperCase();

    if (method !== "GET" && method !== "HEAD") {
        headers.set("X-CSRFToken", getCookie("csrftoken"));
    }

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: "same-origin",
    });

    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || `Request to ${url} failed with ${response.status}`);
    }

    return response.json();
}
