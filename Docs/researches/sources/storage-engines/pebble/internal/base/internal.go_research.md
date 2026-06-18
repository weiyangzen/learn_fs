# sources/storage-engines/pebble/internal/base/internal.go

Purpose: Defines Pebble's core internal key model: sequence numbers, key kinds, trailers, key encoding/decoding, visibility, internal key/value pairs, atomic sequence numbers, compact key bounds, and storage-tier constants.

APIs and types: Key exports include `SeqNum`, `SeqNumRange`, `InternalKeyKind`, `InternalKeyTrailer`, `InternalKey`, `InternalKV`, `KVMeta`, `AtomicSeqNum`, `InternalKeyBounds`, `StorageTier`, constructors/parsers (`MakeInternalKey`, `MakeSearchKey`, `DecodeInternalKey`, `ParseInternalKey`, `ParseInternalKV`, `ParseInternalKeyRange`), and ordering/visibility helpers (`InternalCompare`, `Visible`, `IsExclusiveSentinel`).

Control flow and state: Internal keys sort by user key ascending, then trailer descending so newer versions and higher kinds sort first. `Visible` handles committed and batch sequence spaces, with `SeqNumMax` always visible for sentinels. `Separator` and `Successor` use comparer-provided functions and fall back to original keys unless the shortened user key remains ordered correctly. `InternalKeyBounds` stores two user keys in one immutable string and exposes slices using `unsafe`.

Persistence and dependencies: The trailer layout is durable: 7-byte sequence number plus 1-byte kind, encoded little-endian. Key kind constants are file-format sensitive. Depends on binary encoding, atomics, `invariants`, redact formatting, and comparer callbacks.

Integration points: This file underpins memtables, SSTables, WAL batches, manifest metadata, iterators, compaction, range tombstones, range keys, blob/tiering metadata, and tests/tools parsing debug strings.

Risks: Changing key-kind values or trailer semantics breaks on-disk compatibility. Unsafe string-backed bounds must not be mutated. Parser helpers panic on invalid debug input. Visibility semantics around batch bits and sentinels are subtle and correctness-critical.

Test signals: `internal_test.go` covers encoding, invalid keys, comparer order, kind roundtrips, separators, and exclusive sentinel detection.
