<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_fuzzer.cc -->
# sources/storage-engines/rocksdb/fuzz/db_fuzzer.cc

## Purpose

`db_fuzzer.cc` is a byte-oriented libFuzzer harness that interprets input as a sequence of RocksDB API operations against a temporary DB. Its goal is sanitizer-driven discovery of memory safety, undefined behavior, and API-state bugs across basic DB operations, iteration, snapshots, column families, compaction, and reopen paths.

## Important APIs, Types, and Functions

- `OperationType` enumerates supported operations: put, get, delete, property read, iterator, snapshot, open/close, column family, compact range, seek-for-prev, and count.
- `LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)` is the libFuzzer entry point.
- It uses `FuzzedDataProvider` to consume random-length strings for keys, values, properties, and range bounds.
- RocksDB APIs exercised include `DB::Open`, `Put`, `Get`, `Delete`, `GetProperty`, `NewIterator`, `GetSnapshot`, `ReleaseSnapshot`, `Close`, `CreateColumnFamily`, multi-CF `Open`, `DropColumnFamily`, `DestroyColumnFamilyHandle`, `CompactRange`, `SeekForPrev`, and `DestroyDB`.

## Control Flow

The harness opens `/tmp/testdb` with `create_if_missing=true`, then sets `max_iter` from the first input byte and loops over at most `size` operations. Each iteration maps the current byte to an `OperationType` and consumes additional strings from `FuzzedDataProvider` as needed. Some operations intentionally ignore returned statuses. The column-family case creates `new_cf`, closes/reopens the DB with both default and new column families, performs a put/get/drop on the second handle, destroys handles, and falls back to a normal reopen if multi-CF open fails. At the end it closes and destroys the DB.

## State and Persistence Behavior

The fuzzer creates durable temporary state under `/tmp/testdb` for each input and destroys it at the end. Reopen and column-family operations deliberately persist manifest/data state across closes within one fuzz iteration. Snapshot and iterator operations exercise in-memory references, but the snapshot case releases the snapshot before deleting the iterator, which is an aggressive lifetime pattern for sanitizer coverage.

## Dependencies and Integration Points

It depends on libFuzzer's `FuzzedDataProvider` and RocksDB public `DB` APIs. It is built by `fuzz/Makefile` and linked against RocksDB. It integrates broad public API state transitions rather than checking semantic equivalence.

## Risks and Edge Cases

The harness reads `data[0]` without first checking `size > 0`, so empty inputs can trigger an out-of-bounds read in the harness itself. It uses a fixed `/tmp/testdb`, which is problematic for parallel fuzzer processes or stale preexisting state. Several statuses and possibly uninitialized handles are not defensively checked, especially in the column-family branch after `CreateColumnFamily`. The snapshot branch releases a snapshot before iterator deletion, which may or may not match intended API lifetime but is useful as a stress case.

## Test Signals

Signals are sanitizer findings, crashes, hangs, leaks, and assertion failures from random API sequences. Useful harness-health checks include running with an empty input, parallel corpus execution, and detecting leftover `/tmp/testdb` after failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_fuzzer.cc -->
