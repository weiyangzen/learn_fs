# sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter.go

## Purpose
This file implements `fragmentIter`, an adapter from a row-block point iterator to `keyspan.FragmentIterator`. It reads range deletion and range key blocks where fragmented internal keys with identical bounds are stored as adjacent entries, and reconstructs them into `keyspan.Span` values.

## Important APIs, Types, And Functions
`fragmentIter` holds a row-block `Iter`, suffix comparator, reusable key/span buffers, direction state, file number for tracing, synthetic prefix/suffix transforms, and an invariant close checker. `NewFragmentIter` initializes the underlying block iterator with fragment transforms, using the block iterator for synthetic prefix handling on start keys and the fragment iterator for end keys. `initSpan`, `addToSpan`, and `applySpanTransforms` decode rangedel/rangekey entries and apply synthetic prefix/suffix rules. `gatherForward` and `gatherBackward` collect adjacent entries with the same start key, sort span keys by trailer, and leave the inner iterator positioned just beyond the gathered span. Public methods implement `First`, `Last`, `Next`, `Prev`, `SeekGE`, `SeekLT`, `Close`, `SetContext`, `String`, `WrapChildren`, and `TreeStepsNode`.

## Control Flow
Forward gathering initializes a span from the current KV, advances while the next internal key has the same start bound, adds each fragment, applies transforms, sorts keys, and returns the span while the block iterator is positioned at the first key of the next span. Backward gathering mirrors this by stepping backward through identical bounds and leaving the iterator at the last key of the previous span. `Next` and `Prev` include direction-switching logic to compensate for those deliberate post-gather positions. `SeekGE` finds the span before `k` with `SeekLT`, returns it if it covers `k`, otherwise advances to the next span.

## State And Persistence Behavior
The iterator persists no bytes; it aliases block data where safe and copies start/end keys when synthetic prefixes or invariants-mode stress require stable buffers. Returned spans are only stable until the next positioning call, and the `Keys` slice may be reused. `Close` closes the inner iterator, clears transient state, and returns the object to `fragmentBlockIterPool` except on some invariant-checking paths.

## Dependencies And Integration Points
The implementation depends on `rowblk.Iter`, `keyspan`, `rangedel`, `rangekey`, `blockiter.FragmentTransforms`, block buffer handles, invariant finalizers, and `treesteps`. It is used by SSTable readers for raw range deletion and raw range key blocks. The restart interval assumption of 1 for range blocks is part of the memory lifetime contract because it avoids prefix-compressed unstable keys.

## Risks
Direction switching is subtle because the inner block iterator is intentionally left outside the returned span. Synthetic prefix/suffix handling can accidentally alias unstable buffers or apply invalid suffixes to unsupported range key kinds. `SeekGE` is implemented via `SeekLT` plus `Next`, which is correct but can do extra work and depends on span end comparisons. Close/pool reuse must clear buffers and handles to avoid leaks or stale data.

## Test Signals
`rowblk_fragment_iter_test.go` exercises datadriven span building, iteration, seeking, direction switches, synthetic sequence numbers, prefixes, suffixes, and invariant-only cases. Reader virtual range-del/range-key tests in `reader_test.go` provide integration coverage through SSTable-level APIs.
