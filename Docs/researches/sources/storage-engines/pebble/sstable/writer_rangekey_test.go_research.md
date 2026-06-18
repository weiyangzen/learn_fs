# sources/storage-engines/pebble/sstable/writer_rangekey_test.go

## Purpose
Datadriven tests for public `Writer` range-key APIs across supported table formats.

## Important APIs, Types, And Functions
`TestWriter_RangeKeys` builds SSTables from datadriven `SET`, `UNSET`, and `DEL` commands, then reads raw range-key spans. It uses `testkeys.Comparer`, `colblk.DefaultKeySchema`, `NewWriter`, `RangeKeySet`, `RangeKeyUnset`, `RangeKeyDelete`, and `NewRawRangeKeyIter`.

## Control Flow
For each table format from Pebble v2 through max, a `build` command writes range-key operations to an in-memory SST. After each operation, the input byte slices are scrambled to detect incorrect caller-slice retention. The table is closed, reopened, and raw range-key spans are iterated and printed.

## State And Persistence Behavior
Each build creates an in-memory SSTable. The writer's internal range-key copy buffer is implicitly validated by scrambling original slices after calls.

## Dependencies And Integration Points
Exercises `Writer` range-key fragmentation, key schema selection, row/column format differences, reader range-key iterators, datadriven testdata, and virtual filesystem.

## Risks And Edge Cases
The test depends on datadriven expected output for fragmented/coalesced spans. It focuses on range keys and does not mix point keys or range deletions in the same built table.

## Test Signals
Exact datadriven output, absence of slice-aliasing corruption, and successful iteration across all table formats are the signals.
