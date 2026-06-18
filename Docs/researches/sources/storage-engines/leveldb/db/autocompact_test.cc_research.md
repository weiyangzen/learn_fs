<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/autocompact_test.cc -->
# sources/storage-engines/leveldb/db/autocompact_test.cc

## Purpose
GoogleTest coverage for automatic compaction triggered by reads over deleted data ranges.

## Important APIs, Types, And Functions
Fixture `AutoCompactTest` owns DB path, tiny LRU cache, Options, and DB pointer; helpers `Key()`, `Size()`, and `DoReads(int)`; tests `ReadAll` and `ReadHalf`.

## Control Flow
Constructor opens a no-compression DB with a 100-byte cache. `DoReads()` writes ~100 MB of 200 KB values, compacts memtable, deletes all keys, compacts again, records approximate sizes, repeatedly scans the target key range until size drops by 10x, then verifies untouched range size remains close.

## State And Persistence Behavior
Creates/destroys a temp DB named `autocompact_test`; mutates on-disk tables and tombstones; uses `DBImpl::TEST_CompactMemTable()` for internal flushing.

## Dependencies And Integration Points
Depends on gtest, `DBImpl`, public DB/cache APIs, and test macros/utilities. Included in `leveldb_tests` for non-shared builds, validating interaction between reads, cache pressure, approximate sizes, and compaction scheduling.

## Risks
Uses sleep/poll loop up to 100 seconds, so slow or overloaded environments can be flaky; relies on internal DBImpl casting and approximate size heuristics.

## Test Signals
`ReadAll` and `ReadHalf` confirm read-triggered compaction reduces touched range while leaving other range approximately unchanged.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/autocompact_test.cc -->
