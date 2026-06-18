# sources/object-store/rustfs/crates/targets/src/config/loader.rs

## Purpose
Target config collection and merge engine. It reads RustFS config-file sections and `RUSTFS_*` environment variables, applies default and instance overrides, redacts sensitive values for debug logging, and emits enabled target configs for runtime creation.

## Important APIs, types, and functions
- `collect_target_configs` and `collect_target_configs_from_env` return enabled `(instance_id, KVS)` pairs for a target type.
- `collect_env_target_instance_ids*` discovers explicit env instance ids without materializing configs.
- `collect_merged_target_configs_from_env` is the core merger and returns `MergedTargetConfigRecord` with effective config plus source flags.
- `is_sensitive_target_field`, `redact_target_field_value`, and `redacted_target_config` protect passwords, tokens, credentials, private keys, and DSNs in debug logs.

## Control flow
The loader filters env vars to the RustFS prefix, reads file configs from a section such as `notify_webhook`, extracts file default `_`, then parses env keys using the route prefix, target type, and valid-field set. Env default overrides extend file defaults. The instance list starts from file instance ids and adds env instance ids only when their env config contains `enable`. For each instance, effective config is file/env default, then file instance, then env instance; finally enabled state is derived from the merged result.

## State and persistence behavior
No persistence occurs. Effective `KVS` values are cloned and merged in memory. The loader deliberately preserves redacted debug observability without mutating the real config values passed to target builders.

## Dependencies and integration points
It depends on `rustfs_config` naming constants, `KVS`/`Config`, tracing, and `common.rs` helpers. `plugin.rs` uses `collect_target_configs` to create registered targets from server config; `instance.rs` uses the crate-private merged-record function to keep disabled/admin-visible records.

## Risks and edge cases
Only env-only instances with an explicit instance `enable` key are discovered, so setting only `endpoint_INSTANCE` is ignored even if the default is enabled. Field parsing is strict against the valid-field list and logs ignored fields. Redaction must track new secret-bearing field names; otherwise debug logs could expose credentials.

## Test signals
Tests cover env defaults applying to file targets, env instance discovery with `enable`, env-only instances without `enable` being skipped, fields with internal underscores, Redis field parsing, sensitive-value redaction, partial MySQL/Postgres DSN redaction, and redacted config shape preservation.
