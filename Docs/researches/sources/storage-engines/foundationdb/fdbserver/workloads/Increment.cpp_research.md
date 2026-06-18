# sources/storage-engines/foundationdb/fdbserver/workloads/Increment.cpp

## Purpose
Atomic-operation throughput and consistency workload. It repeatedly increments one key in each half of a keyspace and verifies that the aggregate sums remain equal.

## Important APIs, types, and functions
`Increment` derives from `TestWorkload`, exposes `intToTestKey`, `incrementClient`, `incrementCheckData`, and `incrementCheck`, and tracks transactions, retries, transaction-too-old retries, commit-failed retries, and latency.

## Control flow
Each client starts `actorCount` Poisson-paced actors for `testDuration`. Each actor creates a transaction, performs two `MutationRef::AddValue` atomic ops with `"\x01"` against random keys in opposite halves of the configured range, commits with retry handling, and records latency. Check gathers client errors, enforces minimum throughput, and on client 0 reads the whole keyspace to validate sums.

## State and persistence behavior
State is a set of numeric little-endian atomic-add values under decimal string keys. The workload never initializes or clears keys; absent keys count as zero. It reads all keys at check time and decodes values up to `uint64_t`.

## Dependencies and integration points
Uses native transactions, atomic add mutation semantics, tester timing helpers, and normal retry behavior through `Transaction::onError`.

## Risks and test signals
Risks include 32-bit `int` sum overflow if very high transaction counts are configured, reliance on atomic add byte encoding, and false failures under intentional fault injection if expected rate is too high. Signals are client future errors, minimum throughput warnings/failures, and equality of first-half and second-half sums.
