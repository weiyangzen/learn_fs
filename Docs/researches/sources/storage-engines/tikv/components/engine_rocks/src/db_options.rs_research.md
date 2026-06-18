<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_options.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/db_options.rs

Purpose: wraps RocksDB database and Titan database option objects behind `engine_traits` option traits.

Important APIs/types/functions: `RocksDbOptions`, `RocksTitanDbOptions`, `DbOptionsExt for RocksEngine`, `DbOptions for RocksDbOptions`, and `TitanCfOptions for RocksTitanDbOptions`. The wrappers expose raw conversion, deref access, rate limiter mutation, write-buffer-manager flush controls, Titan option installation, WAL manifest verification, and background job inspection.

Control flow: `RocksEngine::get_db_options` snapshots raw options from the live DB; `set_db_options` forwards string option pairs to RocksDB. Mutators check optional RocksDB subcomponents such as rate limiter and write buffer manager and return errors if absent.

State and persistence behavior: changes affect live DB behavior and, for options RocksDB persists in manifests or option files, future recovery semantics. Rate limiter and write buffer manager mutations alter shared runtime state.

Dependencies/integration: bridges `engine_traits::{DbOptions, DbOptionsExt, TitanCfOptions}` to `rocksdb::{DBOptions, TitanDBOptions}`.

Risks: missing subcomponents produce runtime errors; deref exposes raw option methods, so callers can bypass trait-level invariants. `set_db_options` relies on RocksDB string validation.

Test signals: no local tests in this file; coverage is indirect through engine construction, import, flush, and Titan tests in neighboring modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_options.rs -->
