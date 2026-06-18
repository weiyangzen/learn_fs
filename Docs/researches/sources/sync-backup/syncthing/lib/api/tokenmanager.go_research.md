# sources/sync-backup/syncthing/lib/api/tokenmanager.go

Purpose: Bounded persistent token storage and cookie session management for API auth and CSRF.

Important APIs/types/functions: `tokenManager` stores tokens in an `apiproto.TokenSet`, backed by misc DB. Methods are `Check`, `New`, `newExpiryNanos`, `Delete`, `saveLocked`, and `scheduledSave`. `tokenCookieManager` wraps session cookie naming, creation, validation, deletion, and `sessionCookieMaxAge`.

Control flow: `newTokenManager` best-effort loads a token set from DB. `Check` validates presence and expiry, refreshes sliding expiry, and schedules save. `New` creates a random token and schedules save. `saveLocked` removes expired tokens, enforces max count by oldest expiry, and debounce-schedules DB persistence one second after inactivity. Cookie creation detects HTTPS directly or through reverse-proxy headers and sets Secure when connection or GUI TLS warrants it.

State and persistence behavior: Token state is held in memory and persisted to misc DB keys such as `sessions` and `csrfTokens` through delayed protobuf marshaling. Session cookies are browser-side state with configurable path, persistence, max age, and secure flag.

Dependencies and integration points: Used by auth middleware and CSRF manager. Depends on misc DB, generated `apiproto.TokenSet`, protobuf marshaling, config GUI settings, event logging, and random token generation.

Risks: Persistence is best effort and delayed; crashes can lose very recent token changes. Sorting eviction by expiry treats no-expiry tokens as oldest (`0`) and can evict them first when over limit. Cookie deletion uses the path from the incoming cookie; historical multiple-path cookies are handled by iterating all same-name cookies.

Test signals: `api_auth_test.go` covers token validity, max item eviction, sliding expiry, no-expiry behavior, and negative session-cookie duration. `api_test.go` covers login/logout cookie lifecycle.
