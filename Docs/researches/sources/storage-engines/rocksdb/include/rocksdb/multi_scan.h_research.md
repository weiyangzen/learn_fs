# Research: sources/storage-engines/rocksdb/include/rocksdb/multi_scan.h

## Purpose

`multi_scan.h` declares an experimental range-scan container API that iterates over multiple ordered scan ranges using standard input-iterator style. It presents a nested iteration model: `MultiScan` yields `Scan` objects, and each `Scan` yields key/value pairs for one range.

## Important APIs, Types, and Functions

The header defines `MultiScanException`, `Scan`, `Scan::ScanIterator`, `MultiScan`, and `MultiScan::MultiScanIterator`. `MultiScanException` wraps a non-OK `Status`. `ScanIterator` yields `std::pair<Slice, Slice>` from an underlying `Iterator`, checks status after advancing, and throws on invalid dereference or scan errors. `MultiScan` owns read options, scan arguments, DB and column-family pointers, an upper-bound slice, and a unique DB iterator.

## Control Flow

Callers create `MultiScan` through `DB::NewMultiScan`, then loop over scans and over key/value pairs. Construction creates a DB iterator, configures the first range upper bound, and calls `Iterator::Prepare(scan_opts)` unless mixed bounded/unbounded ranges force a slow path. `MultiScanIterator` seeks to the start key of the current range in its constructor. Incrementing the outer iterator checks current status, advances the range index, updates or clears `iterate_upper_bound`, recreates the DB iterator if bound presence changes, seeks the next start key, and throws on errors.

## State and Persistence Behavior

The API stores only scan execution state. It does not persist data. Returned slices are backed by the underlying iterator and follow normal iterator lifetime rules. `read_options_` is copied and mutated internally for per-range upper bounds. The `upper_bound_` member owns storage for the current bound because `ReadOptions::iterate_upper_bound` points to it.

## Dependencies and Integration Points

The header depends on `db.h`, `iterator.h`, and `options.h`. The implementation lives in `db/multi_scan.cc` and checks filesystem async-I/O support before honoring `MultiScanArgs::use_async_io`. Integration points include `DB::NewMultiScan`, `MultiScanArgs` and `ScanOptions` in `options.h`, block-based table MultiScan prefetch, `IODispatcher`, read-scoped block buffers, user-defined indexes, statistics tickers/histograms, and external table tests.

## Risks and Edge Cases

The interface is experimental and throws exceptions, unlike most RocksDB APIs that return `Status`. Empty scan vectors, missing start keys, invalid dereference, and out-of-range advancement throw logic errors or status exceptions. Mixed ranges with and without limits skip Prepare and recreate iterators on bound-mode changes. HISTORY shows recent fixes for upper-bound respect, page unpinning, async fallback, max sequential skip, dictionary compression fallback, and incorrect results across files, so boundary and ownership behavior are high risk.

## Test Signals

Signals include `table/table_test.cc` DBMultiScan and block-based MultiScan validation, user-defined-index MultiScan failure tests, `util/io_dispatcher_test.cc` MultiScan read-scoped provider coverage, statistics counters/histograms, and HISTORY regression cases. Tests should assert range ordering, correct start/limit behavior, no cross-range leakage, expected exceptions/statuses, async fallback when unsupported, bounded prefetch memory, and valid slice contents until iterator advancement.
