# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkloadKeys.h

## Purpose
This header declares helpers for mapping floating-point positions to deterministic test keys and back.

## Important APIs, Types, And Functions
`doubleToTestKey(double p)` and `testKeyToDouble(const KeyRef& p)` convert between a double and a key. Prefix overloads `doubleToTestKey(double p, const KeyRef& prefix)` and `testKeyToDouble(const KeyRef& p, const KeyRef& prefix)` scope the conversion under a key prefix.

## Control Flow
Workloads choose numeric positions, convert them to ordered keys, and later decode keys back into numeric positions for validation or distribution logic.

## State And Persistence Behavior
There is no state. Generated keys may be written by workloads and therefore must be stable across processes and runs.

## Dependencies And Integration Points
It depends only on FDB key types. It integrates with simulation workloads, consistency checks, and benchmark keyspace generation.

## Risks And Edge Cases
Floating-point precision, ordering preservation, prefix stripping, and invalid key inputs are the main risks. The conversion must be deterministic across platforms.

## Test Signals
Tests should verify round trips, monotonic ordering, prefix behavior, boundary values, and malformed input handling.
