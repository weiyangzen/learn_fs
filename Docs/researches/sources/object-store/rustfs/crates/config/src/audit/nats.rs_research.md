# sources/object-store/rustfs/crates/config/src/audit/nats.rs

## Purpose
Declares NATS audit target environment variables and valid config keys.

## Important APIs, types, and functions
Exports env constants for enablement, server address, subject, username/password, token, credentials file, TLS CA/client cert/client key/required flag, queue directory, and queue limit. `AUDIT_NATS_KEYS` mirrors those config keys and includes comments.

## Control flow
No runtime flow; consumers use static slices for parsing and validation.

## State and persistence behavior
All state is compile-time metadata.

## Dependencies and integration points
References shared NATS key constants from the config crate and is re-exported by `audit/mod.rs`.

## Risks and edge cases
Multiple auth mechanisms can be configured simultaneously; conflict resolution is outside this file. TLS-required semantics and credential file readability are downstream concerns. Array lengths are manually maintained.

## Test signals
No local tests; integration tests should cover env/config loading for each auth mode.
