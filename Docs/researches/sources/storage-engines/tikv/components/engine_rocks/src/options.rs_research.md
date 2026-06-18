<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/options.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/options.rs

Purpose: converts engine-trait read, write, and iterator options into RocksDB raw option objects.

Important APIs/types/functions: `RocksReadOptions`, `RocksWriteOptions`, `build_read_opts`, and `TsFilter`.

Control flow: read conversion sets fill-cache; write conversion sets sync, no-slowdown, WAL disable, and disables memtable insert hints. Iterator conversion configures fill-cache, max skippable internal keys, Titan key-only, total-order or prefix seek modes, adaptive readahead, timestamp table filtering, and lower/upper bounds.

State and persistence behavior: options are per-operation and do not persist state. They affect cache pollution, WAL durability, iterator table pruning, and RocksDB read/write behavior.

Dependencies/integration: consumed by `engine.rs`, `engine_iterator.rs`, write-batch code, and MVCC timestamp-aware scans.

Risks: timestamp filtering hard-codes `tikv.min_ts` and `tikv.max_ts` property names. Decode failures in table filter fall through to include the table, preserving correctness but weakening pruning.

Test signals: no direct tests here; exercised through iterator scans, raft log fetches, MVCC property tests, and query paths using timestamp hints.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/options.rs -->
