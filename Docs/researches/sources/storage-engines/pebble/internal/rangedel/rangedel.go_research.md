# sources/storage-engines/pebble/internal/rangedel/rangedel.go

## Purpose
This file implements encoding, decoding, and point-iterator interleaving support for Pebble range deletion tombstones (`RANGEDEL`). Range deletions are represented as `keyspan.Span` values internally and as internal key/value pairs on disk.

## Important APIs, Types, and Functions
`Encode` emits one internal key/value pair per range deletion key in a span, requiring every key kind to be `InternalKeyKindRangeDelete`; it uses the span start as the internal user key and the span end as the value. `Decode` creates a span from one encoded key/value pair and appends to an optional key buffer. `DecodeIntoSpan` appends another key into an existing span after checking start and end consistency. `Interleave` wraps a point iterator and range deletion iterator in a pooled `keyspan.InterleavingIter`, returning both the iterator and a `TombstoneSpanGetter`; if no range deletion iterator exists, it returns the point iterator unchanged. `interleavingIter.Close` returns wrappers to a sync pool.

## Control Flow and State
Encoding loops over span keys and aborts on kind mismatch or emit error. Decoding is allocation-conscious through caller-provided key buffers. `DecodeIntoSpan` performs invariant-only start matching but always validates the end key because input can come from disk. Interleaving initializes a pooled wrapper with `InterleaveEndKeys: true`, making range deletion boundaries visible in the internal iteration stream. Persistent state is only the encoded key/value representation; runtime state is pooled and reset on close.

## Dependencies and Integration
The file depends on `base`, `invariants`, `keyspan`, and `sync`. It is an integration bridge between sstable/raw internal key encoding and the generic keyspan iterator machinery used by Pebble compactions and reads.

## Risks and Edge Cases
`Encode` rejects non-range-delete keys with a corruption error, protecting on-disk format generation. `Decode` aliases `ik.UserKey` and `v`, so callers must respect source buffer lifetimes. `DecodeIntoSpan` checks start only under invariants, so production builds rely on callers to group spans correctly. `Interleave` requires the returned iterator to be closed once to avoid pool misuse.

## Test Signals
No direct test file is included in this work item. Coverage likely comes from higher-level range deletion, sstable, and iterator tests. Useful targeted tests would validate corruption errors, buffer aliasing assumptions, and nil range-deletion iterator pass-through.
