# sources/storage-engines/pebble/internal/keyspan/seek_test.go

## Purpose
Tests span seeking helpers over fragmented range deletion spans and snapshot visibility filtering.

## Important APIs, Types, And Functions
`TestSeek` builds spans with `buildSpans`, constructs `NewIter`, optionally attaches probes, selects raw `SeekGE` or `SeekLE`, then applies `Span.Visible(seq)` to the result.

## Control Flow
Datadriven `build` creates and prints fragments. `seek-ge` and `seek-le` parse key/sequence inputs, run the selected seek, handle errors/nil, filter by snapshot sequence, and print spans.

## State And Persistence Behavior
All state is local and in-memory. No persistent files are changed.

## Dependencies And Integration Points
Depends on `datadriven`, `crstrings`, `base.DefaultComparer`, fragmenter test helpers, and probe helpers.

## Risks And Edge Cases
The test focuses on range deletions and visibility after seeking, not every range-key kind or custom comparer.

## Test Signals
Failures indicate predecessor/covering seek mistakes, visibility regression, or error propagation issues.
