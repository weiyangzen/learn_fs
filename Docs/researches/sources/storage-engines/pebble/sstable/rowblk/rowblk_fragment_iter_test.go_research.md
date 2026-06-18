# sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter_test.go

## Purpose
This datadriven test validates row-block fragment iteration for range deletion and range key spans. It builds range-fragment blocks from textual span input, then runs scripted iterator operations and compares formatted span output.

## Important APIs, Types, And Functions
`TestBlockFragmentIterator` is the sole test. It uses `keyspan.Fragmenter` to normalize input spans, `rangedel.Encode` or `rangekey.Encode` to write block entries, row-block `Writer` with restart interval 1, a small Pebble cache to hold the block data, and `NewFragmentIter` to construct the iterator. The `iter` command supports optional `synthetic-seq-num`, `synthetic-prefix`, `synthetic-suffix`, and `invariants-only` arguments. Scripted operations include `first`, `last`, `next`, `prev`, `seek-ge`, and `seek-lt`.

## Control Flow
A `build` command parses each input line as a `keyspan.Span`, fragments overlapping spans, writes encoded range entries into a block, stores the block in cache, and prints the normalized spans. An `iter` command constructs fragment transforms, gets a cached block handle, creates a fragment iterator, then executes each input command while recovering panics into output for invariant-focused cases. Each operation prints the returned span.

## State And Persistence Behavior
The test stores the active block in an in-memory cache value and evicts/frees the previous block on rebuild. It owns cache and block handles carefully, closing them at test teardown. No permanent files are written. The fragment iterator reads from the cached block buffer and is closed after each `iter` command.

## Dependencies And Integration Points
The test integrates `datadriven`, `keyspan.Fragmenter`, range deletion/key encoders, row-block writer/iterator code, block cache handles, synthetic transform structs, `testkeys.Comparer`, and invariant mode. It directly validates the low-level iterator that reader range deletion/range key APIs use.

## Risks
Expected output is sensitive to span string formatting and key ordering by trailer. Panic recovery is intentionally broad for invariant test cases, so non-invariant panics could be rendered rather than immediately crashing if introduced inside a scripted operation. The test assumes range blocks use restart interval 1, matching production encoding.

## Test Signals
Failures indicate incorrect span fragmentation reconstruction, broken direction switching, seek boundary errors, synthetic transform mistakes, or cache/block-handle lifetime problems. Invariant-only cases add stress for invalid synthetic suffix combinations and aliasing assumptions.
