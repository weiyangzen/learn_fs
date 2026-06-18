# sources/user-network-fs/rclone/lib/http/middleware.go

Source read signal: reviewed complete local file (227 lines, sha256 32a9bb94e699ac05).

Purpose: Implements HTTP middleware for basic/htpasswd/custom authentication, TLS-client-certificate usernames, trusted header usernames, CORS, response headers, and base-url stripping.

Important APIs/types/functions: Key functions are `parseAuthorization`, `NewLoggedBasicAuthenticator`, `MiddlewareAuthCertificateUser`, `MiddlewareAuthHtpasswd`, `MiddlewareAuthBasic`, `MiddlewareAuthCustom`, `MiddlewareAuthGetUserFromHeader`, `MiddlewareCORS`, `MiddlewareResponseHeaders`, and `MiddlewareStripPrefix`.

Control flow: Basic-style middleware skips `OPTIONS`, validates credentials, and stores the username in context. Custom auth can consume Basic auth or a user already set by certificate/header middleware. Header auth trims and validates a username regexp. CORS adds configured allow headers/methods, response-header middleware overwrites configured headers, and strip-prefix allows root `OPTIONS` while stripping the configured base path for other requests.

State and persistence behavior: Mostly stateless; `onlyOnceWarningAllowOrigin` logs the wildcard-origin warning once. Auth results are request-context state.

Dependencies and integration points: Uses `go-http-auth`, rclone logging and parsed HTTP options, and context helpers from `context.go`. Installed by `Server.initAuth` and `NewServer`.

Risks and test signals: Header-based auth is only safe behind a trusted proxy. `MiddlewareAuthCertificateUser` assumes `r.TLS` and peer certificates are present. CORS wildcard is explicitly warned; tests cover auth modes, CORS, and custom headers.
