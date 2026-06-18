# sources/sync-backup/kopia/internal/server/server_authz_checks.go

Purpose: implements CSRF token generation/validation and role checks for UI and server-control APIs.

Important APIs/types/functions: `kopiaSessionCookie`, `generateCSRFToken`, `validateCSRFToken`, `requireUIUser`, `requireServerControlUser`, `anyAuthenticatedUser`, and `handlerWillCheckAuthorization`.

Control flow: CSRF tokens are HMAC-SHA256 of the UI session cookie using the auth-cookie signing key and compared in constant time against the API client header. Validation can be disabled by options. Role checks compare Basic Auth username to configured UI or server-control users when authentication is enabled.

State and persistence behavior: relies on session cookie values and server signing key; no persistent storage.

Dependencies and integration points: used by `server.go` request wrappers and static UI index patching.

Risks and test signals: missing UI/control user options deny access when auth is enabled; token correctness depends on stable session cookie. Tests cover token generation and validation.
