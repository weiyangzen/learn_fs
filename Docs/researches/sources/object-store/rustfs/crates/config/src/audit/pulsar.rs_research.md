# sources/object-store/rustfs/crates/config/src/audit/pulsar.rs

## Purpose
Declares Apache Pulsar audit target environment variables and valid config keys.

## Important APIs, types, and functions
Exports env constants for enablement, broker, topic, auth token, username/password, TLS CA, insecure TLS, hostname verification, queue directory, and queue limit. `AUDIT_PULSAR_KEYS` mirrors config keys and includes comments.

## Control flow
No runtime control flow; the file is a schema/key registry.

## State and persistence behavior
All values are static constants.

## Dependencies and integration points
Uses shared Pulsar constants from the config crate and is re-exported by the audit module. Pulsar audit publisher code should use these names for server config and env overrides.

## Risks and edge cases
Auth token and username/password may conflict; resolution is downstream. TLS allow-insecure and hostname verification are sensitive security controls with no validation here. Array lengths must stay synchronized.

## Test signals
No local tests; integration should verify env mapping and TLS/auth validation.
