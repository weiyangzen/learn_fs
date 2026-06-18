# sources/storage-engines/tikv/tests/integrations/storage/test_titan.rs

## Purpose
This file tests TiKV behavior when RocksDB Titan blob storage is enabled, disabled, garbage-collected, and used during snapshot/range deletion flows. It focuses on safe Titan shutdown and avoiding missing-blob or key resurrection problems.

## Important APIs, Types, and Functions
`test_turnoff_titan` uses raftstore cluster helpers, `configure_for_enable_titan`, `configure_for_disable_titan`, RocksDB properties, CF option updates, compaction, and `pre_start_check`. The ignored `test_delete_files_in_range_for_titan` constructs `Engines`, writes raw MVCC keys, ingests an external SST delete, triggers Titan GC, calls `delete_ranges_cfs` with `DeleteFiles`, `DeleteByKey`, and `DeleteBlobs`, builds SST snapshot files, ingests them into another DB, and scans with `ScannerBuilder`.

## Control Flow
The first test writes values into a Titan-enabled cluster, flushes twice, checks L0/blob-file counts, shuts down, verifies startup fails when Titan is disabled prematurely, reopens with Titan, switches `blob_run_mode` to fallback, compacts until blob files are removed, shuts down, and then verifies Titan-disabled startup succeeds after purge. The ignored test creates an overlapped LSM/Titan layout, deletes a range by multiple strategies, builds snapshot SSTs, applies them to a fresh engine, and asserts only key `b` remains visible.

## State, Persistence, and Dependencies
Persistent state is Rocks/Titan data directories, blob files, SST levels, ingested external files, and snapshot SSTs. Dependencies include `engine_rocks`, `engine_traits`, raftstore snapshot helpers, TiKV config builders, and MVCC scanner types.

## Integration Points, Risks, and Test Signals
The tests integrate Titan file lifecycle with TiKV startup checks, compaction, range deletion, snapshot generation, and ingestion. Signals are RocksDB property counts, `pre_start_check` success/failure, and scanner output. The ignored test is valuable but not normally run; it is timing- and storage-layout-sensitive.
