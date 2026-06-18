# sources/storage-engines/rocksdb/db/multi_scan.cc

## Purpose
`multi_scan.cc` implements RocksDB's `MultiScan` wrapper, which scans a sequence of ranges using a DB iterator and optional table-level prepare/prefetch support. It coordinates `ReadOptions::iterate_upper_bound` with each requested scan range and falls back to a slower iterator-recreation path when ranges mix bounded and unbounded scans.

## Important APIs, Types, And Functions
`MultiScan::MultiScan` captures `ReadOptions`, `MultiScanArgs`, `DB*`, and a `ColumnFamilyHandle*`. It normalizes `scan_opts_.use_async_io`: async IO is disabled when the DB file system does not report `FSSupportedOps::kAsyncIO`.

`MultiScanIterator::operator++` advances from one scan range to the next. It checks the underlying iterator status, increments the range index, updates `iterate_upper_bound`, optionally recreates the DB iterator, resets the scan wrapper, and seeks to the next range start.

The implementation uses `db->NewIterator`, `Iterator::Prepare(scan_opts_)`, `Iterator::Seek`, `MultiScanException`, and `MultiScanArgs::GetScanRanges`.

## Control Flow
Construction starts with the first scan range. If that range has a limit, the limit string is copied into `upper_bound_` and `read_options_.iterate_upper_bound` points to it; otherwise the upper bound pointer is cleared. The constructor then checks all scan ranges. If every range either has a limit or every range is unbounded, it can call `Prepare(scan_opts_)` once on the underlying DB iterator. If the set is mixed, it takes the slow path because switching between a non-null and null upper-bound pointer requires creating a new iterator.

Incrementing a `MultiScanIterator` first propagates any non-OK child iterator status as a `MultiScanException`. It then moves to the next scan option. If the next range changes from bounded to unbounded or vice versa, it updates `ReadOptions`, recreates the DB iterator, and calls `scan_.Reset`. If both ranges are bounded, it only overwrites the existing `upper_bound_` value. Finally it seeks to the next range start and throws on seek status failure.

## State And Persistence Behavior
This file has no persistence side effects. It manages transient scan state: the copied read options, the mutable upper-bound string, the current range index, the owned DB iterator, and whether the prepared fast path was available.

The lifetime of `read_options_.iterate_upper_bound` is controlled by `upper_bound_`, avoiding dangling pointers to caller-owned scan arguments. Iterator recreation is used when the upper-bound pointer itself must change between null and non-null.

## Dependencies And Integration Points
The implementation depends on RocksDB public `DB`, `ReadOptions`, `MultiScanArgs`, `ColumnFamilyHandle`, `Iterator`, `FileSystem`, and the helper `CheckFSFeatureSupport` from `file/file_util.h`.

Integration points include `ArenaWrappedDBIter::Init`-style async IO feature checks, DB iterator `Prepare`, block/table multi-scan prefetch paths, and scan-range validation in lower iterator layers.

## Risks
The constructor assumes `scan_opts_.GetScanRanges()[0]` exists; empty `MultiScanArgs` must be rejected before or below this layer. Mixed bounded/unbounded scans intentionally skip `Prepare`, which may reduce performance but avoids invalid iterator state.

Because `iterate_upper_bound` is a pointer in `ReadOptions`, pointer lifetime and pointer/null transitions are delicate. Incorrect reuse could make an iterator consult a stale bound or a non-null pointer for an unbounded range.

## Test Signals
Direct tests are elsewhere in the RocksDB tree, especially table/user-defined-index multi-scan tests. Relevant signals are successful range-by-range iteration, exceptions on invalid child status, correct behavior for mixed bounded/unbounded ranges, no async IO request on file systems without support, and table-level `Prepare` calls only when scan options are compatible.
