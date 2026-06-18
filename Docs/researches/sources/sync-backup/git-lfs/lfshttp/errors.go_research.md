# sources/sync-backup/git-lfs/lfshttp/errors.go

Purpose: Converts HTTP responses into typed Git LFS errors with decoded server messages and status-specific defaults.

Important APIs/types/functions: `IsHTTP`, `ClientError`, `handleResponse`, `statusCodeError`, `NewStatusCodeError`, and `defaultError`.

Control flow: `handleResponse` returns nil for status <400, attempts JSON decode into `ClientError`, falls back to default status messages, then wraps selected statuses as auth, unprocessable, retriable/rate-limit, or fatal errors.

State and persistence behavior: Reads and closes response bodies through `DecodeJSON`. No persistence.

Dependencies and integration points: Used by `Client.do` and redirect handling. Integrates with shared `errors` categories and `lfshttp.DecodeJSON`.

Risks and edge cases: Decoding consumes and closes the response body. Non-JSON error bodies are ignored and replaced with defaults. 500 is fatal except 501, 507, and 509; 429 may become retriable-later based on `Retry-After`.

Test signals: `response_test.go` covers auth/fatal/nonfatal body and no-body paths. Other statuses are not directly tested here.
