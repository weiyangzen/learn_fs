# sources/storage-engines/tikv/tests/integrations/config/mod.rs

## sources/storage-engines/tikv/tests/integrations/config/mod.rs

Purpose: top-level TiKV config integration suite covering TOML round trips, custom fixture deserialization, default/legacy compatibility, renamed keys, readpool behavior, and raft-engine compression threshold adjustment.

Important APIs: `TikvConfig`, `read_file_in_project_dir`, many config structs (`ServerConfig`, `RaftstoreConfig`, `DbConfig`, CF configs, `StorageConfig`, `GcConfig`, `PessimisticTxnConfig`, `CdcConfig`, `ResourceControlConfig`, etc.), `toml::{to_string_pretty, from_str}`, `compatible_adjust`, `logger_compatible_adjust`, and `validate`.

Control flow: `test_toml_serde` round-trips defaults. `test_serde_custom_tikv_config` constructs a large expected `TikvConfig`, reads `integrations/config/test-custom.toml`, optimizes split settings, compares with debug equality, and round-trips the loaded config. Later tests assert empty and section-only default TOML equals defaults, partial readpool sections preserve defaults, legacy readpool settings disable unified pool, old per-CF block-cache sizes are combined into shared cache capacity, old root log keys migrate into `[log]`, renamed server/storage keys deserialize equivalently, and raft-engine compression threshold is adjusted only when async raftstore IO is enabled and the threshold was default.

State and persistence: reads TOML fixtures from project root; otherwise in-memory serde/validation. No writes.

Dependencies and integration points: broad TiKV config schema, RocksDB/Titan/raft-engine enums, encryption/security, backup/log-backup/import/gc/cdc/resolved-ts/split/resource-control modules. Risks are high schema churn, deprecated compatibility paths, fixture drift, and equality failures from default changes. Test signals are exhaustive equality checks and explicit compatibility assertions.
