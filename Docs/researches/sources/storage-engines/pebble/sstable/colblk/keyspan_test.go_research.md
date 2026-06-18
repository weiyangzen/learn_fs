<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan_test.go -->
# sources/storage-engines/pebble/sstable/colblk/keyspan_test.go

## Purpose
`keyspan_test.go` validates columnar keyspan block encoding, decoding, iteration, iterator pooling, cache-handle behavior, and range-deletion performance.

## Important APIs, Types, And Functions
`TestKeyspanBlock` is datadriven over `testdata/keyspan_block`. `TestKeyspanBlockPooling` exercises `NewKeyspanIter`, `KeyspanIter.Close`, and cache-backed metadata. `BenchmarkKeyspanBlock_RangeDeletions` and `benchmarkKeyspanBlockRangeDeletions` measure seek and next performance across span/key counts and key sizes.

## Control Flow
Datadriven commands include `init`, `reset`, `add`, `finish`, and `iter`. `add` parses span lines, `finish` reports unsafe boundary keys and debug formatting, and `iter` initializes a non-pooled `keyspanIter` with optional synthetic seqnum/prefix/suffix transforms before running `keyspan.RunFragmentIteratorCmd`. The pooling test builds a two-span block, stores initialized decoder metadata in a cache value, and concurrently obtains handles, iterates first/next/exhaustion, and closes.

## State And Persistence Behavior
Tests persist blocks in memory and, for pooling, inside Pebble's cache allocation with block metadata initialized in place. They verify that iterator pooling does not retain live handles after close and that cached decoder metadata can be shared across concurrent read-only iterators.

## Dependencies And Integration Points
The file uses `internal/keyspan`, `internal/cache`, `testkeys.Comparer`, `sstable/block`, `sstable/blockiter`, `datadriven`, and `testify/require`. The benchmark reflects range-deletion workloads.

## Risks
Datadriven coverage depends on fragmented, sorted span inputs. The pooling test checks concurrency and handle release, but not transform behavior through `NewKeyspanIter` specifically. Benchmarks use generated numeric string keys and may not capture all production key distributions.

## Test Signals
Signals include golden block debug output, fragment-iterator command transcripts, boundary key reporting, successful concurrent pooled iteration, and benchmark metrics including average bytes per row.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan_test.go -->
