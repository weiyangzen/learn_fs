<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/server_config.rs -->
# sources/object-store/rustfs/crates/config/src/server_config.rs

## Purpose
Provides the in-memory server configuration model for KVS-based subsystem configuration plus global default and active config registries.

## Important APIs, types, and functions
`KV` stores `key`, `value`, and `hidden_if_empty` with serde alias `hiddenIfEmpty`. `KVS(Vec<KV>)` supports `new`, `get`, `lookup`, `is_empty`, `keys`, `insert`, and `extend`. `Config(HashMap<String, HashMap<String, KVS>>)` supports `new`, `get_value`, `set_defaults`, `unmarshal`, `marshal`, and placeholder `merge`. Globals are `DEFAULT_KVS: OnceLock<HashMap<String, KVS>>` and `GLOBAL_SERVER_CONFIG: RwLock<Option<Config>>`; public helpers register defaults and get/set the global config.

## Control flow
`Config::new` creates an empty map then calls `set_defaults`. `set_defaults` inserts each registered subsystem default under `DEFAULT_DELIMITER` when missing. JSON unmarshal loads the nested map and reapplies defaults; marshal serializes the internal map shape. KVS insert updates existing keys in place or appends new `KV` values.

## State and persistence behavior
Default KVS registration is one-shot via `OnceLock`. Active server config is process-global, mutable behind an `RwLock`, and cloned on reads. Persistence is JSON bytes produced/consumed by `marshal` and `unmarshal`; no file I/O occurs here.

## Dependencies and integration points
Integrates with admin config subsystems, feature-gated `server-config-model`, serde JSON storage, global runtime configuration readers, and constants such as `COMMENT_KEY` and `DEFAULT_DELIMITER`.

## Risks and edge cases
`register_default_kvs` ignores repeated registration failure, so ordering matters and duplicate initialization is silent. `merge` is currently a clone TODO, so default/user overlay semantics may be incomplete. `get` returns empty string for missing keys, which can blur missing versus explicitly empty values. Global config cloning can be stale for callers that cache results.

## Test signals
Unit tests cover KVS lookup/insert/extend/keys, camelCase alias deserialization, JSON marshal/unmarshal shape, `merge` clone behavior, and global config roundtrip. Additional tests should cover default registration ordering and concurrent get/set behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/server_config.rs -->
