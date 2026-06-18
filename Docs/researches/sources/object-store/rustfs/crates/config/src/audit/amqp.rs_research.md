# sources/object-store/rustfs/crates/config/src/audit/amqp.rs

## Purpose
Declares valid config keys and environment variable names for AMQP audit targets.

## Important APIs, types, and functions
`AUDIT_AMQP_KEYS` lists config keys for enablement, URL, exchange, routing, mandatory/persistent flags, credentials, TLS material, queue directory/limit, and comments. `ENV_AUDIT_AMQP_*` constants and `ENV_AUDIT_AMQP_KEYS` provide the environment mapping.

## Control flow
There is no executable control flow; consumers iterate the key slices to validate config or bind env vars.

## State and persistence behavior
All values are compile-time string constants.

## Dependencies and integration points
Depends on shared config key constants such as `AMQP_URL`, `ENABLE_KEY`, and `COMMENT_KEY`. Re-exported by `audit/mod.rs` for audit subsystem parsers.

## Risks and edge cases
The env key array length must stay synchronized with individual constants. Secrets such as password and TLS key are included as env names, so downstream logging must avoid values. Config key and env key order differences could affect code that relies on positional mapping.

## Test signals
No local tests; compile-time references catch renamed shared keys, and integration tests should verify AMQP audit config/env parsing.
