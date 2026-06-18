# sources/object-store/rustfs/crates/config/src/audit/webhook.rs

## Purpose
Declares webhook audit target environment variables and config keys.

## Important APIs, types, and functions
Exports env constants for enablement, endpoint, auth token, queue limit/dir, client cert/key/CA, and skip TLS verify. `AUDIT_WEBHOOK_KEYS` mirrors config keys plus comments.

## Control flow
No executable flow; constants are used for validation and environment binding.

## State and persistence behavior
All values are compile-time strings.

## Dependencies and integration points
References shared webhook key constants and is re-exported by audit aggregation. Webhook target setup uses these keys for endpoint auth, mTLS, CA, queueing, and TLS verification behavior.

## Risks and edge cases
`WEBHOOK_SKIP_TLS_VERIFY` is present in env and config and must be treated carefully. Auth token and TLS key material are sensitive. No validation exists here for URL syntax, certificate paths, or queue limits.

## Test signals
No local tests; webhook audit config parsing and TLS behavior tests are the expected coverage.
