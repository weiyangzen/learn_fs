<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_map_fuzzer.cc -->
# sources/storage-engines/rocksdb/fuzz/db_map_fuzzer.cc

## Purpose

`db_map_fuzzer.cc` is a protobuf-mutator fuzz harness that compares RocksDB's persisted key/value state against a `std::map` model after a generated sequence of point puts, deletes, and range deletes. Unlike `db_fuzzer.cc`, it checks semantic correctness by reopening the DB and iterating all keys.

## Important APIs, Types, and Functions

- A `PostProcessorRegistration<DBOperations>` normalizes generated `DELETE_RANGE` operations so begin is less than or equal to end according to `BytewiseComparator`.
- `DEFINE_PROTO_FUZZER(DBOperations& input)` is the libprotobuf-mutator entry point.
- The model is `std::map<std::string, std::string> kv`.
- RocksDB APIs exercised include `FileSystem::Default`, `FileExists`, `DB::Open`, `Put`, `Delete`, `DeleteRange`, `Close`, `NewIterator`, iterator seek/next/key/value, and `DestroyDB`.
- `CHECK_OK`, `CHECK_EQ`, and `CHECK_TRUE` macros abort on mismatch.

## Control Flow

The harness ignores empty operation lists, rejects a preexisting `/tmp/db_map_fuzzer_test` path, opens a new DB, and applies each proto operation. PUT updates both DB and map; DELETE removes from both; DELETE_RANGE deletes `[key, value)` in RocksDB and erases the same range in the map. MERGE is defined in the proto but skipped here. After closing and reopening, it iterates RocksDB from first key and compares every key/value pair to the map, then asserts the map is exhausted and destroys the DB.

## State and Persistence Behavior

Each fuzz input creates a temporary persistent DB, closes it, reopens it, validates recovered/manifest state through iteration, and destroys it. The model state is in-memory only. Range deletes are persisted as RocksDB tombstones but modeled as immediate map erasure under bytewise order.

## Dependencies and Integration Points

The harness depends on generated `db_operation.pb.h`, protobuf-mutator macros, RocksDB public DB and filesystem APIs, and `util.h` check macros. It integrates with the fuzz Makefile's proto generation and links with libprotobuf-mutator.

## Risks and Edge Cases

The fixed DB path prevents safe parallel execution and aborts if stale state exists. MERGE operations are silently ignored, which means generated MERGE inputs do not expand semantic coverage. The model assumes default bytewise comparator and default merge/compaction behavior. Range-delete normalization swaps local copies then writes them back, which is correct, but the proto comment says `[key, value]` while the implementation and RocksDB use `[begin, end)`.

## Test Signals

Primary signals are aborts from `CHECK_*` mismatches after reopen, sanitizer crashes, and stale-path aborts. Strong coverage includes mixed PUT/DELETE/DELETE_RANGE sequences, empty and equal range bounds, duplicate keys, keys with embedded nulls, and reopen after many tombstones.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_map_fuzzer.cc -->
