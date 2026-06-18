# sources/sync-backup/syncthing/lib/api/api_auth_test.go

Purpose: Unit tests for static authentication, LDAP template formatting, token expiry/eviction, no-expiry token mode, and session cookie Max-Age behavior.

Important APIs/types/functions: Tests `authStatic`, `formatOptionalPercentS`, `tokenManager`, and `tokenCookieManager.sessionCookieMaxAge`. `mockClock` provides deterministic nanosecond ticking and controlled time jumps.

Control flow: The token manager test creates three tokens, verifies them, creates a fourth to force max-item eviction, advances the clock to test sliding expiry, and verifies expired tokens are rejected. The no-expiry test confirms expiry zero survives long clock advances.

State and persistence behavior: Uses a temporary sqlite misc DB. Token manager save scheduling is asynchronous in production, but tests inspect in-memory token maps and validation behavior.

Dependencies and integration points: Uses `internal/db/sqlite`, misc DB, and config GUI password hashing.

Risks: Tests do not wait for scheduled DB persistence, so they primarily verify in-memory semantics. LDAP network flows are not exercised here.

Test signals: Strong unit signal for static auth, template interpolation edge cases with escaped `%%s`, active-token limit eviction, sliding token lifetime, no-expiry sessions, and negative session-cookie duration.
