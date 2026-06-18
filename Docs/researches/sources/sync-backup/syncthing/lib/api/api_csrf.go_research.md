# sources/sync-backup/syncthing/lib/api/api_csrf.go

Purpose: CSRF protection middleware for REST endpoints and shared API-key header validation.

Important APIs/types/functions: `csrfManager` stores unique cookie/header suffix, protected path prefix, API-key validator, next handler, and token manager. `newCsrfManager` creates a token manager under key `csrfTokens`. `ServeHTTP` enforces token policy. `hasValidAPIKeyHeader` accepts either `X-API-Key` or `Authorization: Bearer`.

Control flow: Valid API keys bypass CSRF and add `Access-Control-Allow-Origin: *`. `/rest/debug` bypasses CSRF. Non-protected paths issue a `CSRF-Token-<unique>` cookie if missing/invalid, then pass through. Protected noauth paths bypass CSRF. All other protected paths require an `X-CSRF-Token-<unique>` header matching a stored token.

State and persistence behavior: CSRF tokens are bounded to 25 active items, expire after one hour, and are persisted by `tokenManager` in misc DB.

Dependencies and integration points: Used by `api.go` before auth wrapping. Depends on GUI config implementing `IsValidAPIKey` and on token persistence in `tokenmanager.go`.

Risks: Debug endpoint bypass is acceptable only because debug routes are separately gated. API-key bypass means API keys are full CSRF bypass credentials, so they must remain secret. Token cookies lack explicit SameSite/Secure attributes here.

Test signals: `TestCSRFRequired` verifies cookie issuance, protected failure without token, success with token, bad API-key failure, and valid API-key/bearer bypass success.
