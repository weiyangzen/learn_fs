# sources/storage-engines/pebble/internal/compact/iterator_test.go

## Purpose
This file provides datadriven coverage for `compact.Iter`, including point-key collapse, snapshots, merges, range tombstones, range keys, bottommost compaction, blob references, SETWITHDEL, DELSIZED, and single-delete anomaly callbacks.

## Important APIs, Types, And Functions
`debugMerger` implements `base.ValueMerger`. `TestCompactionIter` parses test KVs/spans, configures `IterConfig`, and prints iterator outputs. `mockBlobValueFetcher`, `decodeBlobReference`, `encodeRemainingHandle`, and `makeInputIters` support lazy blob values and fake iterators.

## Control Flow
Datadriven `define` commands parse point KVs and spans, fragment range deletions, and store input slices. `iter` commands parse snapshot and option arguments, create a new compaction iterator, run `first`/`next` steps from input, print keys, values, spans, pinned/force-obsolete flags, missized counts, and callback side effects.

## State And Persistence Behavior
The tests do not write persistent DB state. They model compaction input streams in memory and validate the exact transformed stream that would be persisted by the runner.

## Dependencies And Integration Points
The file uses `datadriven`, `sstable.ParseTestKVsAndSpans`, `keyspan.Fragmenter`, `rangekey`, fake internal iterators, `valblk` handle encoding, and the compaction iterator API.

## Risks And Edge Cases
The tests are high-value because iterator behavior is easy to regress with small algorithm changes. Remaining risk is that datadriven fixtures must encode every important sequence; randomized stress is not present here.

## Test Signals
Exact textual output from `testdata/iter`, `iter_set_with_del`, and `iter_delete_sized` is the primary signal. Callback summaries catch ineffectual or nondeterministic single deletes and missized deletes.
