<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/logger.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/logger.rs

Purpose: routes RocksDB info-log messages into TiKV structured logging.

Important APIs/types/functions: `RocksdbLogger`, `TabletLogger`, and `RaftDbLogger`, each implementing `rocksdb::Logger`.

Control flow: `logv` maps RocksDB log levels to TiKV `crit`, `error`, `warn`, `info`, or `debug` macros. `TabletLogger` prefixes each message with a tablet name; raft DB logs use raft-specific targets.

State and persistence behavior: no persistent state except `TabletLogger`'s tablet name string. Affects observability, not RocksDB data.

Dependencies/integration: installed into RocksDB options elsewhere; depends on `rocksdb::Logger` and `tikv_util` logging macros.

Risks: unknown log levels are ignored. Raw RocksDB log text is passed through, so noisy logs or sensitive paths may surface in TiKV logs.

Test signals: no direct tests; behavior is observable through RocksDB logging integration in runtime deployments.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/logger.rs -->
