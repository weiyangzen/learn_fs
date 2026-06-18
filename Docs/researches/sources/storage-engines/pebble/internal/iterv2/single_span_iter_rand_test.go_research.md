# sources/storage-engines/pebble/internal/iterv2/single_span_iter_rand_test.go

## Purpose
`single_span_iter_rand_test.go` randomized-tests `SingleSpanIter` against the general `TestIter` reference implementation.

## Important APIs, Types, And Functions
`TestSingleSpanIterRandom` runs 200 seeds. `runSingleSpanRandomTest` chooses a random key config, random non-empty span, random range-delete trailer, random dynamic bounds, initializes `SingleSpanIter`, and calls `CheckIter`.

## Control Flow
The test loops until it has two distinct random keys for span start/end, orders them, chooses a sequence number, computes bounds, and runs 500 random operations. On failure it logs seed, config, span, trailer kind, and bounds.

## State And Persistence Behavior
All state is seed-local. No golden files are used; reproducibility is via the logged seed.

## Dependencies And Integration Points
It depends on `math/rand/v2`, `base`, `keyspan`, `testkeys`, and iterv2 test utilities.

## Risks And Edge Cases
Random coverage is probabilistic but broad across bounds, prefixes, and operation sequences. The expected data contains exactly one span and no points, matching the optimized iterator’s contract.

## Test Signals
Passing runs signal that `SingleSpanIter` matches general span-boundary semantics for seeking, movement, exhaustion, and bounds.
