# sources/storage-engines/rocksdb/options/db_options.h

Purpose: declares RocksDB's internal DB option snapshots. `ImmutableDBOptions` captures fields that are fixed after open, while `MutableDBOptions` captures DB-level fields that can be adjusted through the mutable-options pipeline.

Important APIs, types, and functions: `ImmutableDBOptions` exposes constructors from default `DBOptions` or an existing `DBOptions`, `Dump(Logger*)`, WAL directory helpers, and a broad set of DB-level fields including creation flags, file system/environment objects, WAL controls, logging, cache, checksum, compaction service, follower catchup knobs, and write temperatures. `MutableDBOptions` exposes analogous constructors and `Dump(Logger*)` for runtime-tunable fields such as background jobs, WAL size, sync rates, manifest limits, stats cadence, off-peak window, and SST open behavior. Free functions serialize, parse, and compare mutable DB options.

Control flow: callers create snapshots from public `DBOptions`, pass them through configurable helpers for parsing or comparison, and rebuild a public `DBOptions` using functions declared in `options_helper.h`. WAL helper methods choose either the explicit `wal_dir` or the first DB path/default path supplied by the caller.

State and persistence behavior: this header is state-definition only, but it establishes persistence boundaries. Immutable fields are usually written to options files as DB options and are not expected to change live. Mutable fields can be serialized with `GetStringFromMutableDBOptions` and parsed from maps for dynamic updates. Convenience members (`fs`, `clock`, `stats`, `logger`) are derived, not independent persisted options.

Dependencies and integration points: includes `rocksdb/options.h` and references `SystemClock`, `Logger`, `Env`, `RateLimiter`, `SstFileManager`, `Statistics`, `WriteBufferManager`, `EventListener`, `Cache`, `WalFilter`, `FileChecksumGenFactory`, and `CompactionService`. It is consumed by `db_options.cc`, `options_helper.cc`, parser verification, DB open/reconfiguration paths, and diagnostic dump paths.

Risks: the struct declarations must stay synchronized with static option metadata in `db_options.cc`, copy/build functions in `options_helper.cc`, and all-fields settable tests. Adding fields without updating those locations can silently break options-file persistence, dynamic configuration, or byte-coverage tests. Direct access to `wal_dir` can be wrong; callers should use `GetWalDir`/`IsWalDirSameAsDBPath` as the comment states.

Test signals: the main direct signal is `DBOptionsAllFieldsSettable`, which enumerates excluded non-scalar fields and asserts string parsing plus snapshot rebuild covers the rest. Parser round-trip tests elsewhere also depend on these declarations matching the registered option maps.
