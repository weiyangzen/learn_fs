# sources/sync-backup/git-lfs/lfsapi/response_test.go

Purpose: Tests API response error classification and message extraction for auth, fatal, and nonfatal server statuses.

Important APIs/types/functions: Uses `Client.Do`, `lfshttp.handleResponse`, `lfshttp.DecodeJSON`, `errors.IsAuthError`, and `errors.IsFatalError`.

Control flow: Test servers return specific status codes with or without JSON bodies. Tests assert wrapped error category and resulting message or prefix.

State and persistence behavior: No persistent state; each test uses temporary HTTP servers and in-memory counters.

Dependencies and integration points: Connects `lfsapi.Client` pass-through `Do` to `lfshttp` response classification and JSON error decoding.

Risks and edge cases: Covers 401, 500, 501, 507, and 509. It does not cover 422, 429 retry-after, 403/404 default errors, or invalid JSON bodies.

Test signals: Good signal that JSON `message` bodies override default messages and empty bodies get status-specific fallbacks.
