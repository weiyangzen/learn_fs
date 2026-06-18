# sources/storage-engines/pebble/internal/manifest/marked_for_compaction.go

## Purpose
`marked_for_compaction.go` implements an ordered set of tables that have been marked for compaction, commonly from upgrade or manifest state. It gives compaction picking a deterministic priority order.

## Important APIs, Types, And Functions
- `MarkedForCompactionSet` wraps a generic Google B-tree keyed by `tableAndLevel`.
- Ordering is decreasing LSM level, then increasing table `SeqNums.High`, then increasing table number.
- `Count`, `Insert`, `Delete`, `Contains`, `Clone`, and `Ascending` provide set operations and ordered iteration.

## Control Flow
The set lazily allocates its B-tree on first insert. `Insert` uses `ReplaceOrInsert` and panics under invariants if the table-level pair already existed. `Ascending` wraps B-tree ascent in an `iter.Seq2`.

## State And Persistence Behavior
The set is in-memory state inside `Version` and `BulkVersionEdit`. Marks are persisted by `VersionEdit.TablesMarkedForCompaction` records and reconstructed/updated during `BulkVersionEdit.Accumulate` and `Apply`.

## Dependencies And Integration Points
It depends on `TableMetadata`, `base.TableNum`, `github.com/google/btree`, and invariants. `VersionEdit` decodes/encodes mark records, and `BulkVersionEdit` deletes marks when tables are deleted while carrying marks into the new `Version`.

## Risks And Test Signals
The priority order is subtle: highest levels are processed first, with older/lower high sequence numbers earlier within a level. Duplicate inserts are caught only in invariant builds. Version edit tests cover parse/encode/apply paths for compaction marks.
