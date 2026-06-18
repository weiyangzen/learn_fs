# sources/storage-engines/pebble/internal/keyspan/span.go

## Purpose
Defines the core in-memory representation for range deletions and range keys over user-key intervals.

## Important APIs, Types, And Functions
`Span` holds inclusive `Start`, exclusive `End`, `[]Key`, and `KeysOrder`. `Key` holds trailer, suffix, and value. Major methods include `Valid`, `Empty`, `Bounds`, `SmallestKey`, `LargestKey`, sequence-number accessors, `Visible`, `VisibleAt`, `Covers`, `CoversAt`, `Clone`, `Contains`, `Reset`, `CopyFrom`, formatting, sorting helpers, and `ParseSpan`.

## Control Flow
Visibility scans trailer-desc keys and handles batch sequence numbers specially as always visible because batch span keys are filtered earlier. `Visible` may return a subslice or allocate when visible batch keys and visible committed keys sandwich invisible keys. Bounds/key methods panic if trailer-desc ordering is required but absent. Sorting helpers use Go `slices.SortFunc`.

## State And Persistence Behavior
`Span` and `Key` are in-memory values with borrowed or cloned byte slices depending on caller choice. `CopyFrom` and `Clone` deep-copy key/suffix/value buffers; `Reset` retains buffers for reuse. No persistence occurs.

## Dependencies And Integration Points
Depends on `base` internal key trailers/kinds, suffix comparison, formatters, `slices`, and `errors`. This type is shared by memtables, sstable range-key/range-delete blocks, fragmenters, merging iterators, and public iterator state.

## Risks And Edge Cases
Key ordering is critical: many methods panic or misbehave if `KeysOrder` is not `ByTrailerDesc`. Batch sequence handling is subtle. `ParseSpan` is test-only and panics on malformed input. Slice ownership must be clear because many iterators return transient spans.

## Test Signals
`span_test.go` covers parsing roundtrip, `Visible`, `VisibleAt`, and `CoversAt`. Many other iterator tests indirectly exercise formatting, sorting, and bounds helpers.
