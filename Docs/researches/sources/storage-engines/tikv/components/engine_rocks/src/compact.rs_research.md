# sources/storage-engines/tikv/components/engine_rocks/src/compact.rs

Purpose: Implements manual compaction operations for `RocksEngine`.

Important APIs and types: `RocksEngine` implements `CompactExt`, with `RocksCompactedEvent` as event type. Methods include `auto_compactions_is_disabled`, `compact_range_cf`, `compact_files_in_range_cf`, `compact_files_cf`, and `check_in_range`.

Control flow: Auto-compaction status iterates CFs and returns true if any CF disables auto compactions. Range compaction builds `CompactOptions` from `ManualCompactionOptions` and calls RocksDB. File-in-range compaction scans CF metadata levels below the output level, selects files overlapping the requested key range, and delegates to `compact_files_cf`. File compaction determines output level, output compression, target file size, optionally filters out L0 files, builds `CompactionOptions`, and calls RocksDB.

State and persistence behavior: Operations mutate RocksDB SST layout but not logical key-value content. Output compression and file sizing are derived from live CF options.

Dependencies and integration: Uses CF name discovery, CF-handle lookup, RocksDB metadata/options, CPU count for subcompactions, and error mapping. Called by administrative compaction and split/check maintenance.

Risks: Range overlap tests use byte comparisons against file smallest/largest keys; boundary semantics must match RocksDB metadata. `exclude_l0` filters by filename suffix, which depends on RocksDB naming conventions. Large compactions can be expensive and run concurrently depending on options.

Test signals: `test_compact_files_in_range` creates multiple L0 files per CF with auto compaction disabled, compacts selected ranges to L1 and then the last level, and asserts file distribution and key ranges.
