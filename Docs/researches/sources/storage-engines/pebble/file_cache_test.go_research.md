# sources/storage-engines/pebble/file_cache_test.go

## Purpose
Exercises Pebble's `FileCache` and `fileCacheHandle` behavior across table readers, blob file readers, shared cache ownership, virtual SSTable bounds, context cancellation, retry paths, leak detection, and fatal diagnostics. The tests fabricate many SST and blob objects in a memory filesystem and assert that the file cache opens files lazily, closes them exactly once, respects capacity, and remains correct under concurrent use.

## Important APIs, Types, And Functions
`fileCacheTestFS` wraps `vfs.FS` to count opens/closes, inject open errors, and delay opens. `fileCacheTestFile.Close` increments close counts. `fileCacheTest` owns a block cache handle and `FileCache`, builds test SST/blob objects through `objstorageprovider`, and constructs `fileCacheHandle`s with `newHandle`. `fileByIdx`, `validateOpenFiles`, `validateNoneStillOpen`, and `validateAndCloseHandle` are the main test helpers. Test coverage centers on `newIters`, `GetValueReader`, `Evict`, `findOrCreateTable`, `FileCache.Ref`, `FileCache.Unref`, and DB-level reads through `DB.newIters`/`DB.Get`.

## Control Flow
The shared fixture creates 200 SSTables and 100 blob files, then resets open/close counters before returning a cache handle. Random-access tests spawn or serialize thousands of iterator opens, verify `SeekGE("k")` finds the expected value length, and close iterators. Frequently-used tests repeatedly touch pinned files and rotating files, expecting pinned files to remain open. Eviction tests randomly read files and explicitly evict a small range, then compare average open counts for evicted versus safe files. Cancellation tests slow `Open`, run many goroutines with canceled, timed-out, or live contexts, and accept context errors only for callers whose contexts were canceled. Virtual-read tests manually replace a physical L6 table with two virtual table metadata entries and then verify point/range-delete/range-key reads through the file cache.

## State And Persistence Behavior
No production persistent state is intentionally created beyond in-memory DB/SST/blob files. The tests track transient cache state through reference counts, open/close maps, cached table/blob readers, reader iterator refs, and virtual table metadata. `TestVirtualReadsWiring` writes a manifest edit to replace one table with virtual SSTables and uses `checkVirtualBounds` to ensure metadata bounds match actual iterated keys. `TestFileCacheEvictClose` verifies object deletion events after compaction and close report no file-removal errors. `TestFileCacheNoSuchFileError` deletes an SST under an open DB and verifies the fatal message includes a useful directory summary.

## Dependencies And Integration Points
The file integrates `cache.Cache`, `FileCache`, `objstorageprovider`, `sstable.Writer`, `blob.FileWriter`, `manifest.TableMetadata`, virtual table backing metadata, `vfs.NewMem`, `base.MakeFilepath`, and DB operations such as `Open`, `Flush`, `Compact`, `NewIter`, and `Get`. It also exercises range-key and range-deletion iterator construction, table format handling, `block.InitFileReadStats`, corruption wrapping, and the event listener path for deleted tables.

## Risks And Edge Cases
The suite targets high-risk cache bugs: double-close or leaked file handles, use after all references are released, shared cache behavior with multiple DBs, iterator leaks during cache close, cached error poisoning after failed opens, context cancellation racing with shared initialization, bad magic number corruption messages, missing-table fatal diagnostics, and virtual SSTable bound mistakes. Several tests rely on timing/backoff or randomized access, so flakes may expose real races but can also require careful seed analysis.

## Test Signals
The file is itself the test signal. Strong signals are exact reference-count panics, `validateOpenFiles` capacity and close-count checks, leaktest failures, successful virtual reads over split metadata, expected injected-error retry behavior, accepted context cancellation outcomes, fatal logger capture for missing files, and benchmarks for iterator allocation and cache hot paths.
