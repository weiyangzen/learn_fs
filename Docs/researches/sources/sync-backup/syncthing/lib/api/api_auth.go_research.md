# sources/sync-backup/syncthing/lib/api/api_auth.go

Purpose: Authentication middleware and helpers for GUI/API access, supporting API keys, session cookies, Basic auth, JSON password login, static bcrypt credentials, and LDAP.

Important APIs/types/functions: Constants bound active sessions, random token length, and login body size. `emitLoginAttempt`, `remoteAddress`, `antiBruteForceSleep`, `unauthorized`, `forbidden`, and `isNoAuthPath` support audit events and responses. `basicAuthAndSessionMiddleware` implements `ServeHTTP`, `passwordAuthHandler`, and logout handling. `attemptBasicAuth`, `auth`, `authStatic`, `authLDAP`, `formatOptionalPercentS`, and `iso88591ToUTF8` implement credential checks.

Control flow: Middleware accepts valid API-key headers first, then valid session cookies, then Basic auth. Successful Basic auth creates a non-persistent session cookie. Public paths and static assets are allowed after auth attempts. If protected and unauthenticated, it returns either 401 with a Basic realm or 403 depending on config. JSON password login is limited to 1 KiB, creates a session on success, and sleeps 100-199 ms on failure. LDAP auth dials plain/TLS/StartTLS, binds with interpolated DN, and optionally searches for exactly one matching user.

State and persistence behavior: Session persistence is delegated to `tokenCookieManager` and misc DB. Login attempts are emitted to the event logger. Failed credentials are logged with redacted structured metadata.

Dependencies and integration points: Integrates with config GUI and LDAP config, event logging, random jitter, IP parsing utilities, and `tokenmanager.go`. Used from `api.go` around the full handler chain when GUI auth is enabled.

Risks: Security-sensitive code. Reverse proxy address trust is intentionally limited to loopback/private/link-local/unix-socket peers. LDAP TLS can be configured with insecure verification. `formatOptionalPercentS` uses `fmt.Sprintf` with counted `%s`; malformed templates with other formatting directives could still behave unexpectedly. Basic auth ISO-8859-1 fallback preserves compatibility but expands accepted credential encodings.

Test signals: `api_test.go` covers Basic, API-key, bearer, session cookie, logout, UTF-8 and ISO-8859-1 credentials, noauth exceptions, and password-change invalidation. `api_auth_test.go` covers static auth and percent-s formatting.
