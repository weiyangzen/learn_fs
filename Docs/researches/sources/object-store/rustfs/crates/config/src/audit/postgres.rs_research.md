# sources/object-store/rustfs/crates/config/src/audit/postgres.rs

## Purpose
Declares PostgreSQL audit target config keys and environment variable names.

## Important APIs, types, and functions
`AUDIT_POSTGRES_KEYS` covers enablement, DSN, table, format, TLS required/CA/client cert/client key, queue directory/limit, and comments. `ENV_AUDIT_POSTGRES_KEYS` groups matching environment variables except comments.

## Control flow
No executable flow; the constants are consumed by config loaders.

## State and persistence behavior
Static strings only.

## Dependencies and integration points
References shared Postgres key constants and is re-exported by audit aggregation. PostgreSQL audit sink setup uses these constants for DSN, TLS, and queue configuration.

## Risks and edge cases
No validation for DSN, table, format, TLS combinations, or queue settings. Secrets must be masked by downstream logging. Manual env array sizing can drift.

## Test signals
No local tests; audit config integration tests should validate accepted keys and environment overrides.
