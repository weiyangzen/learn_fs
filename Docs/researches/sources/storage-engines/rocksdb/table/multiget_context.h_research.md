<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/multiget_context.h -->
# sources/storage-engines/rocksdb/table/multiget_context.h

Purpose: Defines `KeyContext` and `MultiGetContext`, the compact batch state container used to process RocksDB `MultiGet` lookups over sorted subsets of keys.

Important APIs and types: `KeyContext` holds user/internal lookup key views, column family, status, merge context, tombstone coverage sequence, result buffers, timestamp output, and `GetContext`. `MultiGetContext` constructs up to `MAX_BATCH_SIZE` lookup keys, owns stack/heap placement-new `LookupKey` storage, and exposes `GetMultiGetRange()`. `Range` models a subset with skip and invalid bitmasks; `Range::Iterator` walks keys not already skipped, invalidated, or done. Range APIs include `SkipIndex`, `SkipKey`, `MarkKeyDone`, `KeysLeft`, `AddSkipsFrom`, `AddValueSize`, `Suffix`, `operator+=`, `operator-=`, and complement `operator~`.

Control flow: The constructor copies pointers from an `autovector`, materializes `LookupKey`s for the requested slice, and precomputes user-key-with-timestamp, stripped user key, and internal key slices. Lookup stages create ranges and subranges, skip filtered-out keys, mark completed keys in the shared context mask, and optionally combine adjacent/non-overlapping ranges.

State and persistence: All state is per-call runtime state. `value_mask_` is shared across ranges to make completion immediately visible to all iterators. `value_size_` accumulates result size. Lookup keys use stack storage for up to 16 keys and heap storage up to 32 keys. When coroutine support is enabled, an `AsyncFileReader` and `SingleThreadExecutor` are embedded.

Dependencies and integration points: Used by table/cache read paths and `MultiGet` implementations. Depends on `LookupKey`, timestamp stripping, merge context, async reader utilities, statistics, filesystem, and bit-counting helpers.

Risks: Bit operations assume indices below 64 and `MAX_BATCH_SIZE < 64`. Range arithmetic requires non-overlap or containment invariants and uses asserts. `FindLastRemaining()` is subtle for empty masks. KeyContext stores many external pointers, so caller-owned result/status storage must outlive the context.

Test signals: MultiGet batches of 0/1/16/17/32 keys, timestamped reads, range subsetting, skip propagation, done-mask visibility across ranges, range addition/subtraction/complement, value-size accounting, and coroutine-enabled async read execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/multiget_context.h -->
