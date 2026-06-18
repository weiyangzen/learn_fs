# sources/storage-engines/tikv/tests/failpoints/cases/test_engine.rs

Purpose: tests RocksDB engine memory/flush listener behavior in raftstore v2.

Important APIs and functions: `dummy_string` creates zero-filled strings. `test_write_buffer_manager` sets per-CF and global write buffer limits, injects `on_memtable_sealed`, and writes to `CF_WRITE`, `CF_LOCK`, and `CF_DEFAULT`. Ignored `test_rocksdb_listener` models historical memtable sealed/flush ordering around `on_flush_begin`, `on_memtable_sealed`, and `on_flush_completed`.

Control flow: active test lowers write buffer sizes to force memtable sealing and cycles the failpoint return value by CF while writing dummy data. Ignored test splits tablets, starts concurrent flushes, pauses callbacks, and checks no deadlock/panic after RocksDB listener order changes.

State and persistence: writes CF data into tablet/RocksDB engines; listener state tracks memtable flush/seal sequence.

Dependencies and integration: uses `test_raftstore_v2`, `engine_traits::MiscExt`, CF constants, and `ReadableSize`.

Risks and test signals: ignored listener test is scenario documentation. Active signal is write buffer manager interaction with CF-level sealing.
