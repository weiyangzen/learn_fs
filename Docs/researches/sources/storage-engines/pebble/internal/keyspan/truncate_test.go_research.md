# sources/storage-engines/pebble/internal/keyspan/truncate_test.go

## Purpose
Tests bounded clipping behavior of `Truncate` over range deletion span iterators.

## Important APIs, Types, And Functions
`TestTruncate` uses `buildSpans`, `Truncate`, `RunIterCmd`, `formatAlphabeticSpans`, and `require.NoError`. Datadriven commands include `build`, `truncate`, `truncate-and-save-iter`, and `saved-iter`.

## Control Flow
`build` constructs fragmented tombstones. `truncate` creates a truncating iterator for a lower-upper range, walks it forward collecting clones, and formats the result. Saved-iterator commands retain a truncating iterator across subsequent operation scripts to exercise relative movement.

## State And Persistence Behavior
The test holds an in-memory saved iterator and closes it on replacement or test cleanup. No persistent files are modified.

## Dependencies And Integration Points
Depends on `datadriven`, `base.DefaultComparer`, fragmenter test helpers, and `require`.

## Risks And Edge Cases
The test uses exclusive bounds through `UserKeyBoundsEndExclusive`; inclusive-bound assertion behavior is not the main focus here.

## Test Signals
Failures indicate clipping mistakes, incorrect skipping outside bounds, seek correction errors, or relative movement bugs after truncation.
