# sources/storage-engines/pebble/internal/manifest/btree.go

## Purpose
This file implements Pebble's generic copy-on-write B-tree for manifest file metadata. It stores `TableMetadata` or `BlobFileMetadata` in sorted order, supports efficient insert/delete/iteration, shares nodes across version clones, maintains file reference counts, and hosts annotation caches.

## Important APIs, Types, And Functions
`btreeCmp` and specific comparators order tables by sequence number, smallest key, or blob file ID. `fileMetadata` requires `String`, `Ref`, and `Unref`. `node` stores fixed-size items, optional child metadata, refcount, and annotations. `btree` exposes `Clone`, `Release`, `Insert`, `Delete`, `All`, `Count`, and `String`. Internal helpers include `mut`, `clone`, `decRef`, split/rebalance/merge/remove functions, and `verifyInvariants`. `iterator` plus `iterStack` implements first/last/next/prev/find/countLeft/clone/comparison traversal.

## Control Flow
Writes acquire mutable nodes through `mut`; if a node is shared, it is cloned and the old ref is decremented, preserving copy-on-write isolation. Insert splits full nodes on descent and increments item refs before insertion. Delete rebalances or merges underfull children before removal, unreferences the removed item, and collapses an empty root. Release recursively dereferences all contents. Iterators descend/ascend using a compact stack and are invalidated by tree mutation.

## State, Persistence, And Side Effects
The tree is in-memory manifest state, but it determines lifetime of persisted table backings and blob files through `Ref`/`Unref`. Node refcounts are atomic so clones can support concurrent readers and independent writers. Annotation caches live in nodes and are reset when mutable nodes are modified. Tree contents themselves are persisted elsewhere through version edits, not by this data structure.

## Dependencies And Integration Points
The file depends on `cmp`, `bytes`, `fmt`, generic `iter`, `strings`, atomics, CockroachDB errors, and Pebble invariants. It integrates with `LevelMetadata`, `LevelSlice`, `BlobFileSet`, `Version` reference management, obsolete-file tracking, and table/blob annotators.

## Risks And Edge Cases
Refcount correctness is critical: clone and mutation paths must net out item and child refs exactly or files may leak or be deleted early. `assertNoObsoleteFiles` enforces that ordinary tree mutations do not make physical files obsolete; only version release should. Iterator comparisons assume both iterators come from the same root. Writes are not safe for concurrent mutation by multiple goroutines, while reads are safe. Duplicate comparator keys return errors and would violate level invariants if ignored.

## Test Signals
`btree_test.go` covers ordered and reverse inserts/deletes, iterator traversal and clone comparison, seek behavior, duplicate insert errors, concurrent clone isolation, stack behavior, end sentinel behavior, randomized operations, and broad benchmarks. Other files exercise the same tree through level metadata and blob-file sets.
