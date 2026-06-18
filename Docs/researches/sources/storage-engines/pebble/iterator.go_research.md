# sources/storage-engines/pebble/iterator.go

## Purpose
Implements Pebble's public `Iterator`, the user-facing ordered cursor over visible point keys and range keys. It adapts an internal iterator stack over memtables, indexed batches, sstables, range deletions, range keys, and blob values into stable user-key semantics: hiding obsolete versions, applying tombstones, resolving merges, honoring bounds, supporting prefix seeks, exposing range-key metadata, collecting stats, and closing read-state references.

## Important APIs, Types, And Functions
`Iterator` is the central state object. It owns or references the top-level `internalIterator`, `pointIter`, optional `iteratorRangeKeyState`, optional `iteratorBatchState`, read snapshot/version references, current key/value buffers, lazy value fetchers, bounds buffers, read sampling state, stats, and allocation-pool handles.

`iterPos` records how the internal iterator is positioned relative to the external user key: current forward/reverse, one key ahead/behind, or paused at a limited-iteration boundary. `IterValidityState` distinguishes exhausted, valid, and at-limit states. `lastPositioningOpKind` drives seek optimizations. `IteratorStats`, `IteratorMetrics`, `RangeKeyIteratorStats`, `RangeKeyData`, and `LazyValue` are the main exported observation types.

Public positioning methods include `SeekGE`, `SeekGEWithLimit`, `SeekPrefixGE`, `SeekLT`, `SeekLTWithLimit`, `First`, `Last`, `Next`, `NextWithLimit`, `NextPrefix`, `Prev`, and `PrevWithLimit`. Accessors include `Valid`, `Error`, `Key`, `Value`, `ValueAndErr`, `LazyValue`, `HasPointAndRange`, `RangeBounds`, `RangeKeys`, `RangeKeyChanged`, `Metrics`, `Stats`, and `ResetStats`. Lifecycle/configuration APIs include `Close`, `SetBounds`, `SetContext`, `SetOptions`, `Clone`, `CloneWithContext`, and `CanDeterministicallySingleDelete`.

Internal workhorses are `findNextEntry`, `findPrevEntry`, `nextUserKey`, `prevUserKey`, `mergeForward`, `mergeNext`, `nextPointCurrentUserKey`, `saveRangeKey`, `maybeSampleRead`, `sampleRead`, `maybeRefreshBatchView`, `processBounds`, `invalidate`, `iterFirstWithinBounds`, `iterLastWithinBounds`, `internalNext`, and buffer/pool helpers such as `clearForReuse`, `maybeReuseKeyBuf`, and `rangeKeyBuffers.PrepareForReuse`.

## Control Flow
Forward positioning seeks or steps the internal iterator, then `findNextEntry` loops over internal keys. It skips skipped points, ignores delete/single-delete/delete-sized markers, exposes set values, resolves merge chains through `mergeForward`/`mergeNext`, handles interleaved `RangeKeySet` markers, checks optional exclusive limits, saves range-key state, and converts internal exhaustion or errors into external validity.

Reverse positioning flows through `findPrevEntry`. Because reverse iteration sees older versions in the opposite direction, it clones set values before stepping, accumulates merges with `MergeNewer`, treats deletion markers as clearing visibility, preserves range-key boundary-only positions, and only returns when it has determined the newest visible state for the user key. Direction switches are mediated by `iterPos`: `Next` from a reverse-oriented position first moves the internal iterator back onto or past the current key, while `Prev` from a forward-oriented position moves behind the current key and handles ephemeral synthetic range-key positions specially.

Seek operations reset accumulated errors and prefix mode as appropriate, clamp search keys to configured bounds, update stats, and may use no-op or `TrySeekUsingNext` optimizations when repeated monotonic seeks make reuse safe. `SeekPrefixGE` computes a comparer-defined prefix, enters prefix mode, requires `ImmediateSuccessor` when range keys are enabled, and prevents reverse iteration until another absolute non-prefix positioning operation. Limited iteration returns `IterAtLimit` with paused `iterPos` values, but reverse limited iteration may ignore the limit to ensure overlapping range keys can still be surfaced.

Range-key iteration is interleaved with point iteration. `saveRangeKey` copies the current span's bounds, suffixes, and values into iterator-owned buffers only when stale or changed, updates `RangeKeyChanged` state, and records range-key stats. `HasPointAndRange` and `RangeBounds` distinguish point-only, range-only, and combined positions. `NextPrefix` uses a fast next plus internal `NextPrefix` to skip all keys sharing the current comparer prefix, while rejecting cases where a versioned upper bound would make the operation ambiguous.

`SetBounds` and `SetOptions` always make the iterator appear exhausted externally and require absolute repositioning. Internally, `SetOptions` attempts reuse when options and underlying batch state permit, otherwise closes/rebuilds point and range stacks. Indexed-batch iterators call `maybeRefreshBatchView` to advance their batch snapshot when the mutable batch has changed, update range-del/range-key child iterators if possible, and block unsafe seek no-op optimizations via `batchJustRefreshed`.

`Close` tears down the child iterator stack before releasing read state/version refs, merges pending read-compaction samples into the DB queue, closes blob fetchers and value closers, returns range-key state and iterator allocations to pools, and preserves double-close detection. `CloneWithContext` creates an unpositioned iterator over the same read state or manifest version, optionally refreshing an indexed batch view.

## State And Persistence Behavior
The iterator pins transient DB state through either `readState` or `version`, plus optional indexed-batch snapshot sequence state. It does not itself persist data, but it can enqueue read compaction candidates through `maybeSampleRead`/`sampleRead`; `Close` transfers those candidates into `db.mu.compact.readCompactions` and may schedule asynchronous compaction work.

Current key, bounds, prefixes, range-key data, lazy value buffers, and reverse-iteration values are copied into iterator-owned buffers when the underlying iterator's memory would not remain valid. Bounds use a two-buffer scheme so old and new bounds can coexist during internal iterator bound updates. Large buffers are intentionally not retained when returning allocations to pools.

Errors are sticky for relative movement: absolute positioning clears cached iterator errors, while `Next`/`Prev` return without progress if an error is accumulated. `ValueAndErr` may also store an error and exhaust the iterator if lazy value retrieval fails. `requiresReposition` lets `SetBounds`/`SetOptions` hide an internally reusable position from callers until a fresh absolute positioning call.

## Dependencies And Integration Points
This file sits at the boundary between Pebble's public API and internal iterator stack. It depends on `internal/base` for internal key/value types, lazy values, seek flags, and stats; `keyspan`, `keyspanimpl`, and `rangekeystack` for range-key merging/interleaving; `manifest` and `levelIter` for read sampling; `iterv2` and merging iterators for top-level point iteration; `blob` for separated values; `inflight` for iterator tracking; `bytesprofile` for separated-value retrieval profiling; `treesteps` for debug recordings; and `invariants`/`redact` for assertions and safe formatting.

Construction is performed elsewhere by DB, Batch, Snapshot, and external-iterator creation paths through fields such as `finishInitializingIter`, `tableNewIters`, `newIterRangeKey`, and allocation pools. The iterator honors `IterOptions` features including lower/upper bounds, key-type selection, point/range block-property filters, `SkipPoint`, range-key masking, durable-only reads, L6 filters, and external iter validation.

## Risks And Edge Cases
The highest-risk area is the alignment between `iterPos`, `iterValidityState`, `requiresReposition`, and the actual internal iterator position. Direction switches, limited iteration, merge chains, range-key-only synthetic positions, and SetOptions reuse all depend on these invariants. A stale or over-aggressive seek optimization can skip newly visible batch keys or return an earlier/later key than requested.

Range-key handling is subtle because range-key spans are interleaved at start boundaries, can be surfaced without coincident point keys, can mask point keys, and must still be observed across limited reverse iteration. `RangeKeyChanged` depends on `prevPosHadRangeKey`, `stale`, and `updated`, which the source comments identify as intricate.

Prefix iteration has strict contracts: reverse movement is unsupported, limited `Next` with prefix mode is rejected, range-key prefix truncation requires `ImmediateSuccessor`, and bounds must share the requested prefix. `NextPrefix` is barred with versioned upper bounds because MVCC suffix ordering can split versions around the bound.

Memory and lifecycle risks include double-close misuse, returning slices whose contents change on later movement, lazy values whose fetch can fail after `Valid`, open value closers across movements, and long-lived iterators pinning memtables/sstables or blob mappings. `CanDeterministicallySingleDelete` intentionally exposes nondeterministic internal LSM state and is only meaningful once per forward-oriented external position.

## Test Signals
Direct test coverage in the companion files exercises datadriven iterator semantics, forward/reverse stepping, merges and deletes, bounds, stats formatting/merging, read sampling, block-property filters, seek optimization errors, mutable indexed-batch refresh, bounds slice ownership, `SetOptions` equivalence to rebuilding, range-key masking, prefix seek randomized behavior, separated value retrieval profiling, and durable-only reads. Benchmarks stress scan, seek, prefix seek, range-key masking, fragmented range keys, tombstone-heavy workloads, queue-like delete swaths, and block-property filtering.
