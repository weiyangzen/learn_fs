<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raw.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/raw.rs

Purpose: temporarily re-exports selected raw `rocksdb` crate APIs through `engine_rocks`.

Important APIs/types/functions: public re-exports for options, cache, compression/checksum enums, compaction filters/options, event/listener types, env, rate limiter, table property collectors, write buffer manager, perf context, and RocksDB CLI helper functions.

Control flow: no runtime logic; this is compile-time namespace forwarding.

State and persistence behavior: no direct state. Consumers can use re-exported raw types to configure RocksDB state and persistence indirectly.

Dependencies/integration: supports downstream crates during engine abstraction migration so they need not depend directly on `rocksdb`.

Risks: broad raw API exposure weakens abstraction boundaries and can make later backend swaps harder. Re-export list must track RocksDB crate API changes.

Test signals: no direct tests; compile-time users across TiKV validate that required raw symbols remain exported.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raw.rs -->
