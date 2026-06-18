# sources/storage-engines/pebble/merging_iter_v2_rand_test.go

## Purpose
`merging_iter_v2_rand_test.go` performs randomized differential testing of `mergingIterV2`. It generates random levels with point keys, range deletion spans, spurious boundaries, and snapshots, then compares iterator behavior against an independently computed expected point stream through the `iterv2` checker.

## Important APIs, types, and functions
`TestMergingIterV2Rand` runs 200 random seeds. `runMergingIterV2RandomTest` builds the random configuration, expected output, and checker. `randMergingTestLevels` generates level data with non-overlapping per-level sequence-number ranges so LSM ordering assumptions hold.

## Control flow and state behavior
Each run selects a random `iterv2.KeyGenConfig`, constrains sequence numbers, generates up to five levels, and chooses either an all-visible snapshot or a random snapshot. `mergeLevels` from `merging_iter_v2_test.go` computes the expected surviving keys by filtering visible points against visible range deletes. The `mergingIterV2` is wrapped in an `iterv2.InterleavingIter` so the common `iterv2.CheckIter` operation generator can exercise seeks, next/prev, prefix behavior, and `TrySeekUsingNext`.

On failure, the test prints the seed, snapshot, key config, points, and spans, making failures reproducible.

## Dependencies and integration points
The test depends on `iterv2.RandPointKeys`, `iterv2.RandSpans`, `iterv2.CheckIter`, `testkeys.Comparer`, and the test constructor from `merging_iter_v2_test.go`. It explicitly sets `RequirePrefixChangeForTrySeekUsingNext`, matching the invariant enforced by `SeekPrefixGEStrict`.

## Risks and test signals
This is a high-value correctness signal for slab logic because it mixes range deletes, snapshots, spurious span boundaries, and random operations. Gaps remain: lower/upper bounds are noted as TODO, and the reference model checks point results rather than internal parking efficiency.
