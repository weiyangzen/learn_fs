<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/config.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/config.rs

Purpose: defines the serializable RocksDB/Titan configuration enums and serde adapters used by TiKV's RocksDB engine layer.

Important APIs/types/functions: `LogLevel`, `CompressionType`, `BlobRunMode`, `compression_type_level_serde`, `compression_type_serde`, `checksum_serde`, `prepopulate_block_cache_serde`, and numeric serde modules for compaction priority, rate limiter mode, compaction style, and recovery mode. `From` and `TryFrom<ConfigValue>` bridge online configuration values to RocksDB/Titan raw enums.

Control flow: deserializers normalize strings, validate enum names and fixed compression-per-level length, then return RocksDB enum values. `BlobRunMode::from_str` accepts both user-facing kebab-case and Titan internal `k*` spellings.

State and persistence behavior: this module holds no runtime state, but its encodings govern persisted config files and online config mutation payloads.

Dependencies/integration: depends on `rocksdb`, `serde`, `online_config::ConfigValue`, and `tikv_util::numeric_enum_serializing_mod`; consumed by higher-level TiKV config structs and option builders.

Risks: panics on non-string `ConfigValue` inputs for compression/blob mode conversions; compatibility depends on keeping spelling aliases stable. Fixed seven-level compression validation will reject any future RocksDB level-count change.

Test signals: unit tests cover compression-per-level TOML serialization, invalid length, and invalid value handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/config.rs -->
