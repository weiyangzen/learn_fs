# sources/storage-engines/pebble/internal/keyspan/test_utils.go

## Purpose
Provides package-local testing facilities for `Span` and `FragmentIterator` implementations.

## Important APIs, Types, And Functions
Probe infrastructure includes `probe`, `probeContext`, `op`, `ErrInjected`, a DSL parser, `ParseAndAttachProbes`, and `probeIterator`. Helpers include `RunIterCmd`, `RunFragmentIteratorCmd`, and `NewInvalidatingIter`. Probe variants inject errors, return custom spans, no-op, log, and branch on predicates like operation kind or start-key equality.

## Control Flow
Probes wrap child iterator operations, observe the operation result, and may replace the span/error before returning. Command runners parse small textual iterator operations and print spans/errors. `invalidatingIter` copies returned spans into owned buffers, corrupts them on the next operation, and thereby catches callers that retain child span memory too long.

## State And Persistence Behavior
All state is test-local: DSL parser definitions, probe context, logs, copied byte buffers, and reusable key slices. No production persistence is touched.

## Dependencies And Integration Points
Depends on Pebble's internal DSL package, `crstrings`, `errors`, `treesteps`, `context`, and reflection. It is shared by many tests in this package and `keyspanimpl`.

## Risks And Edge Cases
Because it lives in the production package, these helpers can access unexported behavior but also increase package build surface for tests. The DSL panics on malformed input, which is suitable for testdata but not external use.

## Test Signals
The helpers themselves are indirectly tested wherever probes and invalidating iterators are used, especially defragmenting, merging, get, seek, and logging tests.
