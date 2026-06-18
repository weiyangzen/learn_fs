# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ReadOptions.java

## Purpose
`ReadOptions` is the primary Java owning wrapper for native `rocksdb::ReadOptions`. It configures reads, point lookups, multigets, iterators, snapshots, bounds, table filtering, timestamp reads, I/O deadlines, caching, readahead, and experimental async I/O.

## Important APIs, Types, And Functions
- Constructors allocate default native options, allocate with `verifyChecksums`/`fillCache`, or shallow-copy another `ReadOptions`.
- Basic read toggles: `verifyChecksums`, `fillCache`, `readTier`, `tailing`, `totalOrderSeek`, `prefixSameAsStart`, `pinData`, `backgroundPurgeOnIteratorCleanup`, `ignoreRangeDeletions`.
- Iterator/read bounds and callbacks: `setIterateLowerBound`, `iterateLowerBound`, `setIterateUpperBound`, `iterateUpperBound`, and `setTableFilter`.
- Snapshot support: `snapshot()` wraps the current native snapshot pointer; `setSnapshot(Snapshot)` stores the native snapshot handle or zero.
- Performance and failure controls: `readaheadSize`, `maxSkippableInternalKeys`, `deadline`, `ioTimeout`, `valueSizeSoftLimit`, and `asyncIo`.
- Timestamp controls: `timestamp`, `setTimestamp`, `iterStartTs`, and `setIterStartTs`.
- Native declarations mirror fields in `rocksdb::ReadOptions` through `options.cc`.

## Control Flow
Every getter/setter asserts the object still owns a native handle and then reads or writes a field on the native `ReadOptions`. Setters return `this` for fluent usage. Bound and timestamp setters pass native `Slice` handles into C++ and retain Java references in private fields to keep owning slice wrappers from being garbage-collected. Getters for bounds create non-owning `Slice` wrappers for C++-owned pointers, while timestamp getters create `Slice` wrappers from raw handles returned by JNI. The copy constructor calls native `copyReadOptions` and then copies Java-side retained references for lower bound, upper bound, timestamp, and iterator start timestamp.

## State And Persistence Behavior
The object owns one native `rocksdb::ReadOptions` allocated with `new` and released through `disposeInternalJni`. Most state lives in the native struct; Java retains only the `AbstractSlice<?>` objects needed for lifetime safety across JNI. The copy constructor is explicitly shallow: snapshot, bound, timestamp, and other native pointers are cloned as pointers, not deep-copied resources. `ReadOptions` is runtime configuration, not persisted database metadata.

## Dependencies And Integration Points
- Extends `RocksObject`.
- Uses `Snapshot`, `ReadTier`, `RocksIterator`, `AbstractSlice`, `Slice`, and `AbstractTableFilter`.
- JNI implementation lives in `java/rocksjni/options.cc` in the `ReadOptions` block and directly maps Java calls to `rocksdb::ReadOptions` fields.
- Used throughout `RocksDB` for `get`, `multiGet`, `keyExists`, `keyMayExist`, `newIterator`, and multi-column-family iterators. Transaction and write-batch-with-index APIs also consume it.
- `TableFilterTest` exercises table-filter callbacks through `setTableFilter`.
- SpotBugs excludes `ReadOptions` from `EI_EXPOSE_REP2` due to deliberate retention of externally supplied slice references.

## Risks And Edge Cases
- Shallow copy means copied options can outlive or share snapshot/slice/table-filter native resources owned elsewhere.
- `setTableFilter` stores a native function object but does not retain the Java `AbstractTableFilter`; callers must keep callback objects alive as long as the options may use them.
- `snapshot()` creates a Java `Snapshot` wrapper around a pointer owned by the DB; releasing snapshots through the wrong owner or using after DB release is dangerous.
- Numeric setters cast Java `long` to native unsigned or size types without Java validation; negative values can become very large native values.
- Deprecated `ignoreRangeDeletions` may disappear; relying on it risks future compatibility breaks.
- Experimental `asyncIo` behavior can change and requires compatible filesystem/table behavior.
- Timestamp APIs are documented as under active development and depend on matching comparator timestamp semantics.

## Test Signals
- `ReadOptionsTest` covers constructor/copy behavior, basic setters/getters, bounds, null bounds, table filters, timestamps, async I/O, and post-close failure behavior.
- Many RocksDB Java tests pass `ReadOptions` through point lookup, multiget, iterator, transaction, and write-batch APIs.
- Additional high-value tests would cover lifecycle of table filters and snapshots, negative numeric values, and timestamp wrapper ownership.
