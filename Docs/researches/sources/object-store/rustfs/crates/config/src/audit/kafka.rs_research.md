# sources/object-store/rustfs/crates/config/src/audit/kafka.rs

## Purpose
Declares Kafka audit target environment variables and valid configuration keys.

## Important APIs, types, and functions
Exports `ENV_AUDIT_KAFKA_*` constants for enablement, brokers, topic, acknowledgements, TLS, SASL, queue directory, and queue limit. `ENV_AUDIT_KAFKA_KEYS` groups env vars; `AUDIT_KAFKA_KEYS` groups config keys plus `COMMENT_KEY`.

## Control flow
No runtime control flow. Config loaders use the slices to whitelist and bind Kafka audit settings.

## State and persistence behavior
All state is static string metadata.

## Dependencies and integration points
References shared Kafka key constants in the config crate and is re-exported by `audit/mod.rs`. Audit target implementation code should use these names to parse server config and environment overrides.

## Risks and edge cases
TLS/SASL credentials are represented by names only, but downstream value handling must be secret-safe. Array sizes must be maintained manually. There is no validation here for broker syntax, ack modes, or SASL mechanism values.

## Test signals
No local tests; integration coverage should verify config/env aliases and invalid key rejection.
