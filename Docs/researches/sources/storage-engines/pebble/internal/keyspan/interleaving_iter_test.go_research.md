# sources/storage-engines/pebble/internal/keyspan/interleaving_iter_test.go

## Purpose
Datadriven tests for `InterleavingIter`, including ordinary point/span interleaving and masking behavior.

## Important APIs, Types, And Functions
`TestInterleavingIter` and `TestInterleavingIter_Masking` call `runInterleavingIterTest`. `maskingHooks` implements `SpanMask`, selecting a suffix threshold from span keys and skipping point keys with larger suffixes. `pointIterator` is a small in-memory `base.InternalIterator` with bounds, seek, prefix, next, and prev support.

## Control Flow
Datadriven commands define spans and point keys, then initialize `InterleavingIter` with optional `masking-threshold` and `interleave-end-keys`. The `iter` command executes first/last/next/prev, seek, prefix seek, next-prefix, and set-bounds commands, printing returned internal keys plus `iter.Span()`.

## State And Persistence Behavior
The test uses local iterator state, prior returned key tracking for `NextPrefix`, and a bytes buffer. No persistence is involved.

## Dependencies And Integration Points
Depends on `datadriven`, `testkeys.Comparer`, `base.InternalKV`, `treesteps`, and `require`. It directly models the point iterator interface consumed by production interleaving.

## Risks And Edge Cases
The hand-written point iterator ignores some advanced production iterator flags, so flag-specific behavior is not covered. The masking test focuses on suffix comparisons in `testkeys` key format.

## Test Signals
Failures reveal ordering mistakes between point keys and synthetic span boundaries, incorrect span truncation under bounds/prefixes, masking callback ordering issues, or direction-switch bugs.
