# sources/storage-engines/pebble/internal/iterv2/interleaving_iter_rand_test.go

## Purpose
`interleaving_iter_rand_test.go` performs randomized differential testing of `InterleavingIter` against the reference `TestIter`.

## Important APIs, Types, And Functions
`TestInterleavingIterRandom` runs 200 random seeds. `runRandomTest` builds random key configs, point keys, non-overlapping spans, optional static start/end bounds, dynamic lower/upper bounds, invalidating wrappers, and an `InterleavingIter`, then calls `CheckIter`.

## Control Flow
For each seed, the test randomly chooses key generation parameters, points/spans, static bounds, dynamic bounds, optional point invalidation, optional nil/invalidating span iterator, initializes the iterator, and runs 500 random operations through `CheckIter`. On failure, deferred logging emits the seed and generated data.

## State And Persistence Behavior
All state is local to a seed. Seeds are logged for reproduction. No golden files are used.

## Dependencies And Integration Points
It depends on `math/rand/v2`, `base`, `invalidating`, `keyspan`, `testkeys`, and the iterv2 random test utilities.

## Risks And Edge Cases
Random coverage is probabilistic and may miss rare arrangements, but seed logging makes failures reproducible. Invalidating wrappers increase sensitivity to unsafe buffer retention.

## Test Signals
Passing random runs signal agreement with the reference model over mixed seeks, movement, prefix mode, bounds, direction switches, spurious nil span iterators, and boundary emission.
