# sources/storage-engines/pebble/internal/batchskl/iterator.go

Purpose: Implements an iterator over the batch skiplist, returning `base.InternalKey` values derived from batch-record offsets.

APIs and types: `Iterator`, internal `splice`, methods `Close`, `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `KeyInfo`, `String`, `SetBounds`, and `seekForBaseSplice`.

Control flow and state: The iterator holds current node offset, cached key, bounds, and cached bound nodes. `SeekGE` optionally tries a bounded number of `Next` steps when `TrySeekUsingNext` is set, otherwise searches the skiplist. Forward methods enforce upper bound; reverse methods enforce lower bound, matching the base iterator contract.

Persistence and dependencies: Iterates in-memory batch storage; no independent persistence. Depends on `batchskl.Skiplist` internals and `base` flags/key types.

Integration points: Used by indexed batches/memtable-like batch iteration. `KeyInfo` maps the current node back to batch record offsets for higher-level batch logic.

Risks: Caller must respect missing lower/upper checks on first/last/seek directions. Iterator state after `SetBounds` is undefined until repositioned. Copy-by-value is supported but shares the same list.

Test signals: `skl_test.go` covers next/prev/seeks/bounds and overflow behavior.
