# sources/storage-engines/tikv/components/engine_rocks/src/cf_options.rs

Purpose: Bridges `engine_traits::CfOptions` to rust-rocksdb `ColumnFamilyOptions`.

Important APIs and types: `RocksEngine` implements `CfOptionsExt::get_options_cf` and `set_options_cf`. `RocksCfOptions` wraps `RawCfOptions`, supports `from_raw`, `into_raw`, deref/deref-mut, write-buffer-manager flush size helpers, and all `CfOptions` trait methods.

Control flow: CF option reads first resolve a CF handle with `util::get_cf_handle`, then obtain raw options from the DB. Dynamic option setting calls RocksDB `set_options_cf`. Trait methods forward to raw RocksDB getters/setters and adapt errors with `r2e` or boxed errors.

State and persistence behavior: `RocksCfOptions` is an in-memory wrapper around raw options. Some setters mutate the option object before engine open; `set_options_cf` changes live RocksDB options. Block cache capacity and compaction limiter setters mutate shared RocksDB objects.

Dependencies and integration: Used by config application, flow-control tuning, compaction setup, block cache management, Titan options, and SST partitioning. Depends on `RocksTitanDbOptions`, `RocksSstPartitionerFactory`, and RocksDB raw APIs.

Risks: `set_flush_size` and `get_flush_size` fail if no write-buffer manager is attached. `set_max_compactions` fails if no compaction-thread limiter exists. Integer casts from RocksDB values to `i32` assume values fit. Dynamic option strings are passed through to RocksDB for validation.

Test signals: No local tests in this file, but compaction tests create and mutate `RocksCfOptions`, and broader engine configuration tests likely cover option bridging.
