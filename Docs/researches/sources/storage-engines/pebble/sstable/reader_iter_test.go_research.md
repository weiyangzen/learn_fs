# sources/storage-engines/pebble/sstable/reader_iter_test.go

## Purpose
`reader_iter_test.go` validates lazy-loading iterator behavior, resource cleanup, concurrent iterator use, boundary cases, stress operations, and bloom-filter optimization behavior for single-level and two-level SSTable iterators.

## Important APIs, Types, and Functions
- `TestIteratorErrorOnInit` checks that lazy index-read errors surface on first iterator use.
- `TestLazyLoadingBasicFunctionality`, `TestLazyLoadingSeekOperations`, and helper functions build small SSTables and verify forward/reverse/seek behavior.
- `TestLazyLoadingResourceManagement`, `TestLazyLoadingResourceCleanup`, and `testMemoryLeakPrevention` exercise close paths and pool/read-handle cleanup.
- `TestLazyLoadingConcurrentAccess` runs many independent iterators against the same reader concurrently.
- `TestLazyLoadingBoundaryConditions` covers empty, single-key, and two-key tables.
- `TestLazyLoadingStressOperations` repeats mixed operations thousands of times.
- `controllableFilterDecoder`, `newControllableFilterPolicy`, `createTestSST`, and `createTestSSTWithOptions` build filter-controlled SSTables.
- Bloom tests cover single-level, two-level, and edge cases around bloom misses.

## Control Flow
The lazy error test writes a one-key SSTable, wraps the file with `errorfs.Toggle`, opens the reader before enabling injection, then creates row single-level or two-level iterators repeatedly. Since index loading is lazy, construction may succeed; `First` should return nil and `Error` should report the injected error.

Basic tests generate deterministic sorted keys, write memfs SSTables in row and column table formats with and without bloom filters, then iterate forward and backward. Seek tests assert `SeekGE` finds exact keys and `SeekLT` returns prior keys.

Resource tests create and close many iterators, close early before/after positioning, and use GC plus memory stats as a heuristic leak detector. Concurrent tests create one iterator per goroutine and perform independent operations against a shared reader.

Bloom tests install a decoder whose `MayContain` return is controlled. They first load a data block, then call `SeekPrefixGE` with a missing prefix. On clean bloom misses, they assert the embedded data iterator remains valid/not invalidated. Two-level tests force partitioning with small block/index sizes and inspect `iter.secondLevel.data`.

## State and Persistence Behavior
Tests persist SSTables in `vfs.NewMem` and reopen them through reader construction. They exercise both writer-side filter policy emission and reader-side filter decoder selection. The tests inspect iterator internal state because they are in package `sstable`, especially `data.Valid`, `IsDataInvalidated`, and two-level second-level state.

## Dependencies and Integration Points
- Uses `NewWriter`, `newReader`, `NewPointIter`, row/two-level constructors, and object-storage file wrappers.
- Uses `block.BufferPool` and `base.InternalIteratorStats` to match production iterator environments.
- Uses `bloom.FilterPolicy`, custom filter decoders, `errorfs`, `vfs`, and `objstorageprovider`.
- Exercises `MakeTrivialReaderProvider` for value-block/lazy-value compatibility even when values are inline.

## Risks and Edge Cases
- Some tests use internal fields and are tightly coupled to iterator implementation details; refactors may need test updates without changing public behavior.
- Memory leak detection is heuristic and may be noisy if runtime allocation behavior changes.
- `controllableFilterDecoder` ignores `mayContainError`; it simulates hit/miss but not decoder errors.
- Concurrent access is safe because each goroutine owns its iterator; it does not make a single iterator concurrently safe.
- Stress operations call `Next`/`Prev` after arbitrary positioning; current iterator API tolerates many but not all invalid sequences, so the test starts positioned and uses a fixed operation cycle.

## Test Signals
The file provides strong regression coverage for lazy index loading, first-use error propagation, data-block preservation on bloom misses, row/column basic operation parity, iterator cleanup, pool reuse, and two-level bloom paths. It complements `random_test.go`, which has broader randomized IO-failure coverage.
