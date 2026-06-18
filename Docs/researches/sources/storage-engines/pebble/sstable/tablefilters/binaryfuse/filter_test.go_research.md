# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter_test.go

## Purpose
Stress-tests binary fuse filter construction over random set sizes up to the configured maximum and verifies sampled inserted hashes always probe as present.

## Important APIs, Types, And Functions
`TestBuildFilter` picks random size ranges with a bias toward 10K and occasional 1M/max-size cases. `testBuild` loads hashes into a `hashCollector`, picks a random supported fingerprint width, builds the filter, and probes up to 100K inserted hashes.

## Control Flow
Each run allocates random hashes, adds them to the collector, calls `buildFilter`, requires success, then randomly samples existing hashes and checks `mayContain`. The test exercises pool, reuse, and large-builder regimes indirectly through randomized sizes.

## State And Persistence Behavior
All state is in-memory hashes and filter bytes. The collector may use pooled hash blocks and builder code may use global pools/semaphores.

## Dependencies And Integration Points
Depends on `math/rand/v2`, `testify/require`, `hashCollector`, `buildFilter`, and `mayContain`. It complements the policy-level end-to-end tests by bypassing key hashing.

## Risks And Edge Cases
The test does not assert false-positive rates or corrupted-input behavior. Random size selection can miss specific boundary values on a given run, but it samples small, medium, large, and max-size regimes.

## Test Signals
Signals are successful filter construction and absence of false negatives for sampled inserted hashes.
