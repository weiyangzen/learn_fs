# sources/storage-engines/pebble/internal/keyspan/fragmenter.go

## Purpose
Implements `Fragmenter`, the eager span fragmentation engine that splits overlapping spans at all overlap boundaries and emits non-overlapping fragments.

## Important APIs, Types, And Functions
`Fragmenter` fields include comparer/formatter, `Emit func(Span)`, pending spans with a shared start, reusable buffers, `flushedKey`, and `finished`. Main methods are `Add`, `Empty`, `Start`, `Truncate`, internal `truncateAndFlush`, `flush`, and `Finish`.

## Control Flow
`Add` requires spans in increasing start-key order and trailer-desc keys. When a new start key exceeds pending start, it truncates/flushed pending spans up to the new start. `truncateAndFlush` splits spans crossing the flush key, emits completed pieces, and retains suffix pieces. `flush` sorts spans by end key, repeatedly emits the next fragment from the common start to the smallest end, aggregates all overlapping keys, sorts keys by trailer descending, and advances remaining start keys to the split.

## State And Persistence Behavior
The fragmenter retains slices supplied through `Add` and allocates fresh key slices for emitted fragments because emitted fragments may be kept indefinitely. It does not write persistent data. `Finish` marks the instance complete and disallows further additions.

## Dependencies And Integration Points
Depends on `base.Compare`, `base.FormatKey`, invariants, `SortSpansByEndKey`, and `SortKeysByTrailer`. It is used by tests, memtable/sstable writing, compaction, and as a reference model for `MergingIter`.

## Risks And Edge Cases
Inputs must be sorted and non-empty spans are expected to have trailer-desc keys. Retaining caller slices is safe for stable memtable/batch spans but risky for unstable sstable iterator buffers unless callers clone appropriately. `Truncate` stores copied flushed keys but `flush` can still emit fragments beyond `lastKey` in compaction-specific scenarios.

## Test Signals
`fragmenter_test.go` covers fragmentation layouts, range-deletion visibility via `Get`/`CoversAt`, range-key values, emit ordering, panic paths, and sorted key emission.
