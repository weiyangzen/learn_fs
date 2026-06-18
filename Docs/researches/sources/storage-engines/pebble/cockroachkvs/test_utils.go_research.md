<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/test_utils.go -->
# sources/storage-engines/pebble/cockroachkvs/test_utils.go

## Purpose
Provides random Cockroach key/value generation utilities shared by tests and benchmarks.

## Important APIs, Types, and Functions
`KeyGenConfig` describes key shape, prefix sharing, average keys per prefix, base wall time, and suffix mix percentages. `KeyGenConfig.String` formats common benchmark names. `RandomKVs` returns sorted keys and random values. `makeMVCCKey`, `cockroachKeyGen`, `makeCockroachKeyGen`, `randRoachKey`, and `randTimestamp` implement generation internals.

## Control Flow
`RandomKVs` constructs a shared prefix, repeatedly generates roach-key prefixes, samples an exponential number of suffixes per prefix, chooses empty/lock/MVCC suffixes according to configured percentages, fills random values, and sorts keys with `Compare`.

## State and Persistence Behavior
No persistent state. Generated keys and values are in-memory fixtures that model Cockroach key distributions for block and SSTable tests.

## Dependencies and Integration Points
Depends on `math/rand/v2`, `slices`, `time`, and Cockroach key encoding/comparison from `cockroachkvs.go`. Used by correctness tests and benchmarks in the same package.

## Risks and Edge Cases
Misconfigured percentages can make empty plus lock suffix probabilities overlap unexpectedly; the code treats `PercentLockSuffix` as the first slice of the combined threshold. `PrefixAlphabetLen` and key lengths must be sensible; invalid zero alphabet length would panic in `IntN`. `AvgKeysPerPrefix` is clamped to at least one generated key per prefix.

## Test Signals
`TestRandKeys`, randomized key-schema tests, columnar block tests, and benchmarks all depend on this helper. Good signals include sorted output, configurable suffix mixes, stable datadriven output under fixed seeds, and broad coverage of prefix/timestamp distributions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/test_utils.go -->
