# sources/storage-engines/rocksdb/util/random_test.cc

## Purpose
Provides regression tests for selected `Random` distribution helpers.

## Important APIs, Types, And Functions
The tests instantiate `ROCKSDB_NAMESPACE::Random` and exercise `Uniform`, `OneIn`, `OneInOpt`, and `PercentTrue`. `main` installs RocksDB's stack trace handler and runs GoogleTest.

## Control Flow
`Uniform` builds histograms for multiple seeds and ranges and checks counts against a loose variance band. `OneIn` counts hits over `average * range` samples and handles range one as deterministic true. `OneInOpt` includes non-positive inputs and expects zero hits for those. `PercentTrue` samples 10,000 times for percentages from negative through above 100 and compares rounded observed percentage.

## State And Persistence
Test state is local counters and vectors. No files or persistent state are written.

## Dependencies And Integration Points
Depends on `util/random.h` and `test_util/testharness.h`. It validates behavior relied on by RocksDB randomized tests and components such as the rate limiter's fairness randomization.

## Risks
Statistical tests are intentionally loose and could miss subtle bias. The `OneInOpt` loop uses `average * range`; for negative ranges the loop count is negative and therefore zero iterations, which matches the expected zero but does not directly call `OneInOpt` with negative inputs. Tests do not cover newer generators or string helpers.

## Test Signals
The file itself is the assigned test signal: distribution bounds for `Uniform`/`OneIn`, boundary behavior for optional probability, and deterministic always-false/always-true behavior for percentages outside `[1, 99]`.
