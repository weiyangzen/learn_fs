# sources/storage-engines/tikv/tests/failpoints/cases/test_debugger.rs

Purpose: validates debug MVCC scanning across tablet-backed region metadata where region ranges and RocksDB key ranges intentionally differ.

Important APIs and functions: `prepare_data_on_disk` builds a TiKV config, tablet registry, raft log engine, six region states, and tablet RocksDB data using `must_prewrite_put`. Region 4 is tombstoned and region 6 has mismatched start/end metadata. `extract_key` maps stored `zkNN` keys to logical `kNN`. `test_scan_mvcc` uses `new_debugger(...).scan_mvcc`.

Control flow: create on-disk raft/tablet metadata, enable `unlimited_range_compaction_filter`, instantiate debugger, reject invalid scans, and verify full and partial scans skip tombstoned or nonmatching regions.

State and persistence: persists raft region local states and per-region tablets on disk. The debugger reads existing files, not a running cluster.

Dependencies and integration: uses `RaftLogEngine`, `TabletRegistry`, `KvEngineFactoryBuilder`, `Debugger`, and storage transaction test helpers.

Risks and test signals: synthetic key mapping is narrow but deliberate. Signal is debug tooling resilience to tombstones, gaps, limits, and bad ranges.
