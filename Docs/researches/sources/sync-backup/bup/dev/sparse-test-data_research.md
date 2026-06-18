# sources/sync-backup/bup/dev/sparse-test-data

## Purpose
Generates randomized test data with zero and nonzero regions around bup sparse-detection thresholds.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`; generator functions include `smaller_region`, `possibly_larger_region`, `initial_region`, `final_region`, and `region_around_min_len`.

## Control Flow
Chooses random output size up to ten read blocks, selects two sparse regions, merges overlap into offsets, alternates writing `x` and NUL byte runs, and logs offsets/write runs to stderr.

## State and Persistence Behavior
Writes a file supplied as the sole argument. Intended output may include holes only semantically as zero bytes, not filesystem sparse holes.

## Dependencies and Integration Points
Supports sparse write/read tests by producing threshold-sensitive byte patterns.

## Risks and Test Signals
Risks include apparent bug in zero-argument handling (`len(argv) == 0` impossible for normal argv) and unseeded randomness. Signals are generated file plus stderr offsets useful for debugging.
