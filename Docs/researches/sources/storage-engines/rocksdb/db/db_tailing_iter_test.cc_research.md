# sources/storage-engines/rocksdb/db/db_tailing_iter_test.cc

## Purpose

This file is a GoogleTest suite for RocksDB tailing iterator behavior. It verifies that iterators created with `ReadOptions::tailing = true` can observe keys appended after iterator construction, continue across memtables and flushed SST files, obey prefix and upper-bound constraints, tolerate deletes and compactions, and preserve correctness when using asynchronous read I/O.

The suite is parameterized over a boolean test parameter. When the parameter is true, each test enables `ReadOptions::async_io`, so most tailing-iterator scenarios run once through the normal iterator path and once through RocksDB's async I/O path. A local `extern "C"` hook, `RocksDbIOUringEnable()`, returns a file-local `enable_io_uring` flag so the async tests can exercise code paths guarded by io_uring availability.

## Important APIs, Types, And Functions

- `DBTestTailingIterator` derives from `DBTestBase` and `::testing::WithParamInterface<bool>`. `DBTestBase` supplies `db_`, column-family handles, helpers such as `Put`, `Delete`, `Flush`, `MoveFilesToLevel`, `CreateAndReopenWithCF`, `ReopenWithColumnFamilies`, and environment flags such as `mem_env_` and `encrypted_env_`.
- `ReadOptions` is configured with `tailing = true` in every test. Many tests also set `async_io`, `iterate_upper_bound`, or `read_tier`.
- `Iterator` is the public RocksDB iterator API under test. The suite exercises `SeekToFirst`, `Seek`, `Next`, `Valid`, `key`, and `status`.
- `ForwardIterator` is reached through `db/forward_iterator.h` and inspected through sync-point callbacks and test-only helpers in `TailingIteratorTrimSeekToNext` and `TailingIteratorUpperBound`.
- `SyncPoint` injects callbacks at internal iterator locations such as `ForwardIterator::SeekInternal:Return`, `ForwardIterator::Next:Return`, `ForwardIterator::RenewIterators:Null`, `ForwardIterator::RenewIterators:Copy`, `ForwardIterator::SeekInternal:Immutable`, and `UpdateResults::io_uring_result`.
- `CompositeEnvWrapper(env_, FileSystem::Default())` is used in many tests to force a real filesystem-backed environment while preserving the configured test environment wrapper.
- `BlockBasedTableOptions` and `NewBlockBasedTableFactory` are used to disable block cache and verify `kBlockCacheTier` incomplete statuses.
- `NewFixedPrefixTransform(2)` and `NewHashSkipListRepFactory(16)` configure prefix-aware storage for the prefix seek test.

## Test Cases And Control Flow

- `TailingIteratorSingle` creates a tailing iterator before any data exists, confirms it is invalid with OK status, writes key `mirko`, seeks again, and verifies the same iterator can see the newly appended key.
- `TailingIteratorKeepAdding` creates a `pikachu` column family and repeatedly appends 10,000 fixed-width keys. After each write it seeks the live tailing iterator to the new key and expects an exact match, proving repeated append visibility without recreating the iterator.
- `TailingIteratorSeekToNext` compares two usage patterns: one iterator repeatedly seeks to a target just before the newly written key, while a second iterator advances by `Next`. It flushes periodically, then repeats descending insertions to cover cases where keys arrive outside simple increasing order.
- `TailingIteratorTrimSeekToNext` is the deepest internal test. It sets a small write buffer, multiple memtables, an upper bound, and three iterators. Sync-point callbacks assert that deleted internal file iterators are handled correctly, that renewed iterator paths hit both null and copy cases, and that the number of active file iterators stays bounded. It later disables the block cache and uses `read_tier = kBlockCacheTier` to require `Status::Incomplete` when data cannot be served from cache, then reopens with normal reads and continues inserting and seeking.
- `TailingIteratorDeletes` reads an initial key, deletes it, writes 10,000 later keys, flushes, advances past the deleted key, and confirms the existing iterator reads exactly the newly appended records.
- `TailingIteratorPrefixSeek` configures a fixed two-byte prefix extractor and hash skiplist memtable. It writes and flushes prefix `01`, writes prefix `02`, and verifies `Seek("0102")` does not incorrectly cross into `0202`, while `Seek("0202")` succeeds.
- `TailingIteratorIncomplete` sets `read_tier = kBlockCacheTier` and allows either a valid cached result or `Status::Incomplete` before and after compaction. This verifies tailing iterators propagate incomplete status rather than incorrectly failing under cache-only reads.
- `TailingIteratorSeekToSame` writes even-numbered keys under universal compaction and verifies that seeking to an already found key keeps the iterator positioned at that key.
- `TailingIteratorUpperBound` sets `iterate_upper_bound = "20"`, flushes keys below and above that bound, adds an above-bound memtable key, and checks that `Next` stops at the bound. It instruments immutable-seek decisions; for normal reads it expects no immutable seek after seeking from an exhausted upper-bound state, while async I/O may report one immutable seek if async read completion was observed.
- `TailingIteratorGap` manually shapes levels with `MoveFilesToLevel` to reproduce a historical gap bug. It builds overlapping/gapped files across levels 1, 2, and 3, then seeks to `30` and expects iteration to continue to `35` and `40` instead of skipping keys that sit in lower-level gaps.
- `SeekWithUpperBoundBug` and `SeekToFirstWithUpperBoundBug` reproduce upper-bound bugs with two L0 files: one visible key `aa` and one out-of-bound key `zz`. They verify both `Seek("aa")` and repeated `SeekToFirst` return `aa` and stop before `zz`.

## State And Persistence Behavior

The tests deliberately move data through RocksDB's persistence states: mutable memtable writes, immutable memtables, flushed SST files, compaction, level movement, and reopen cycles. Most multi-record tests skip in-memory and encrypted environments because they depend on real filesystem behavior, file cache interactions, and internal file iterator lifetimes.

The suite uses column family `pikachu` to isolate most iterator checks from the default column family. Calls to `Flush`, `CompactRange`, `TEST_WaitForCompact`, `ReopenWithColumnFamilies`, and `MoveFilesToLevel` force state transitions that expose bugs hidden by purely in-memory iteration. `TailingIteratorTrimSeekToNext` also checks iterator renewal after old file iterators become obsolete, which is important for long-lived tailing iterators that survive flushes and compactions.

## Dependencies And Integration Points

This file integrates the public RocksDB DB and iterator APIs with internal test utilities. It depends on `db/db_test_util.h` for fixture setup, test DB lifecycle management, column-family helpers, assertions, and level-manipulation helpers. It depends on `db/forward_iterator.h` to make internal `ForwardIterator` objects visible to sync-point callbacks. It depends on `port/stack_trace.h` for crash diagnostics installed in `main`.

The tests exercise interactions among tailing iterators, block-based tables, block-cache-only reads, prefix extractors, hash skiplist memtables, universal compaction, level layout, and async I/O completion. The `UpdateResults::io_uring_result` sync point makes the async parameter meaningful by observing whether the io_uring result path was actually used.

## Risks And Edge Cases Covered

- A tailing iterator must see keys written after iterator creation without requiring a new iterator.
- Deletes must not strand the iterator or hide later keys.
- Prefix seeks must not leak into adjacent prefixes.
- Upper bounds must be enforced across memtables, immutable memtables, L0 files, and repeated `SeekToFirst`.
- Cache-only reads must surface `Incomplete` where appropriate instead of falsely reporting success or corruption.
- Internal file iterators must be renewed or trimmed safely after flushes and compactions, without retaining too many stale iterators.
- Level gaps must not cause tailing iteration to skip keys in lower levels.
- Async I/O can change internal seek accounting, so the upper-bound internal assertion explicitly allows the async path's observed immutable seek when io_uring completion occurred.

## Test Signals

The primary signals are GoogleTest assertions on iterator validity, returned keys, OK statuses, incomplete statuses, and exact record counts. Internal behavior is checked through `SyncPoint` callbacks and `ForwardIterator::TEST_CheckDeletedIters`, which make otherwise invisible iterator-renewal behavior observable. The fixture is instantiated for both `async_io = false` and `async_io = true`, expanding each scenario across synchronous and asynchronous read paths.

The file has its own `main` that installs RocksDB's stack trace handler and runs all GoogleTests, so it can be linked as a standalone test binary within the RocksDB test suite.
