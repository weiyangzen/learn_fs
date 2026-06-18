# sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/end_to_end.go

## Purpose
Provides a shared randomized correctness and coarse-FPR test for table filter policies and decoders.

## Important APIs, Types, And Functions
`RunEndToEndTest(t, policy, decoder, maxFPR)` builds random filters and checks no false negatives plus an upper bound on false positives. `randKey` creates crypto-random keys.

## Control Flow
For ten runs, it chooses a random key count from small to occasional 1M, generates random keys of length 10-19, builds a filter, verifies every inserted key through the decoder, then probes 1000 random non-members and compares the observed rate to `maxFPR`.

## State And Persistence Behavior
Only in-memory keys and filters are used. No SSTable is written.

## Dependencies And Integration Points
Used by Bloom and binary fuse tests. Depends on `base.TableFilterPolicy`, `base.TableFilterDecoder`, crypto random, and `math/rand/v2`.

## Risks And Edge Cases
The FPR bound is deliberately broad and the sample count is small to keep tests fast and non-flaky. Crypto-random generation errors are ignored.

## Test Signals
Signals are successful filter build, no false negatives, and false-positive rate below the caller-provided threshold.
