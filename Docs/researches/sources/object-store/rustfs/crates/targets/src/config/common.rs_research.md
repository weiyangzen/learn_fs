# sources/object-store/rustfs/crates/targets/src/config/common.rs

## Purpose
Shared configuration helpers for target config loading and validation. The module centralizes environment variable field parsing, enable-state parsing, URL parsing, and backend-specific validation that is reused by argument builders.

## Important APIs, types, and functions
- `split_env_field_and_instance` maps an environment-variable suffix to `(field, instance_id)`, including fields that themselves contain underscores.
- `is_target_enabled` reads `enable` from a `KVS` and interprets `EnableState` aliases.
- `parse_target_bool` accepts RustFS enable-state strings and native boolean strings, returning `None` for missing or blank input.
- `validate_nats_server_config` rejects embedded credentials, conflicting auth methods, relative credentials/TLS/queue paths, and unpaired TLS cert/key fields.
- `validate_pulsar_broker_config` validates broker URL, topic presence, mutually exclusive auth styles, TLS option/scheme consistency, and queue directory absoluteness.
- `parse_url` wraps `url::Url::parse` and produces `TargetError::Configuration` with field context.

## Control flow
The env-field splitter normalizes the suffix to lowercase, first checks for a default-instance field match, then finds the longest valid field prefix followed by the default delimiter. NATS and Pulsar validation are fail-fast sequences that read optional keys from `KVS` and return a concrete configuration error at the first incompatible combination.

## State and persistence behavior
No state is persisted. The helpers only read `KVS` values and path strings. They enforce that path-like configuration points to absolute paths before any target runtime writes queue files or loads credentials.

## Dependencies and integration points
The module depends on `rustfs_config` constants and `KVS`, `async_nats::ServerAddr`, Pulsar broker validation from the target module, `url::Url`, and `TargetError`. It is used by `loader.rs` for env parsing and by `target_args.rs` for backend argument validation.

## Risks and edge cases
The longest-prefix logic is important for field names with internal underscores; adding new fields whose names prefix other fields can change parsing unless covered by tests. Boolean parsing is permissive, so callers that need strict `true`/`false` semantics must not assume it. NATS and Pulsar validation use default queue dirs supplied by callers, so an invalid relative default can fail otherwise valid configs.

## Test signals
Tests cover conflicting NATS auth methods, relative NATS queue dirs, and Pulsar TLS flags on non-TLS broker schemes. These are high-value checks because they prevent ambiguous credentials and unsafe TLS settings from reaching runtime connection code.
