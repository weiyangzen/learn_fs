# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse_test.go

## Purpose
Exercises binary fuse filters through the shared table-filter test harness and records benchmark baselines for filter construction and membership queries.

## Important APIs, Types, And Functions
`TestEndToEnd` calls `filtertestutils.RunEndToEndTest` for 4, 8, 10, 12, and 16 bit fingerprints with generous FPR thresholds. `BenchmarkWriter`, `BenchmarkMayContain`, and `BenchmarkMayContainLarge` call shared benchmark helpers using every supported fingerprint size.

## Control Flow
The end-to-end test randomly generates key sets, builds a filter through `FilterPolicy`, verifies every inserted key is reported as present, then probes random non-members and fails if the observed false-positive rate exceeds the supplied threshold. Benchmarks construct filters over fixed key sizes/counts and repeatedly call decoder membership checks.

## State And Persistence Behavior
All state is in-memory filter data and random test keys. No SSTable file is written directly; the test exercises the policy/decoder contract used by table writers.

## Dependencies And Integration Points
Depends on `filtertestutils`, the package `Decoder`, and `SupportedBitsPerFingerprint`. It provides integration confidence for `binary_fuse.go`, `filter.go`, `hash_collector.go`, `writer.go`, and `bitpacking`.

## Risks And Edge Cases
FPR thresholds are intentionally loose to avoid flakes, so they catch gross regressions rather than precise probabilistic drift. Benchmarks document expected performance but are not assertions.

## Test Signals
Signals are no false negatives, FPR below threshold, successful filter creation, and benchmark metrics for MKeys/s and nanosecond membership checks.
