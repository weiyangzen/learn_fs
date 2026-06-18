# sources/test-tools/fio/t/gen-rand.c

## Purpose
Command-line sanity checker for fio's random number helper `rand_between()`. It samples a requested inclusive range and reports whether bucket counts fall within one standard deviation of the expected uniform mean.

## Important APIs, Types, and Functions
Uses `struct frand_state`, `init_rand()`, and `rand_between()` from fio's random library. `main()` parses `start`, `end`, and `nvalues`, allocates bucket counters, computes binomial mean/deviation, and prints pass/fail per bucket.

## Control Flow
After argument and range validation, it initializes deterministic fio random state, loops `nvalues` times, increments the chosen bucket, then evaluates each bucket against `[mean - dev, mean + dev]`.

## State and Persistence Behavior
Only in-memory bucket state exists. Output is human-readable stdout/stderr; no files are written.

## Dependencies and Integration Points
Depends on fio `lib/rand.h`, `lib/types.h`, and `log.h`. It is a statistical smoke test for code used by fio workload generation.

## Risks
One-standard-deviation acceptance is statistically strict for many buckets, so a correct RNG can produce failures. `strtoul()` parsing does not reject trailing garbage. Large ranges or sample counts can allocate large memory or run long.

## Test Signals
Expected signals are argument validation failures for bad ranges and approximately uniform bucket output across common ranges with a sufficiently large sample count.
