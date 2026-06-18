# sources/storage-engines/pebble/external_test.go

## Purpose
Contains broader external/package tests and benchmarks for read error propagation, separated-value lookup performance, restart safety, read-only recovery, and `Options.Clone` independence.

## Important APIs, Types, And Functions
`TestIteratorErrors` uses Pebble metamorphic tests with random read-operation error injection. `BenchmarkPointLookupSeparatedValues` and `buildSeparatedValuesDB` construct value-separation workloads. `TestDoubleRestart`, `getKVs`, and `checkKVs` validate quick close/reopen safety. `TestReadOnlyRecovery` ensures read-only open does not mutate a crash clone. `TestOptionsClone`, `mangle`, and `genVal` fuzz clone isolation.

## Control Flow
Iterator error testing first generates a random DB with write operations, reopens it read-only under an error-injecting FS, then steps through random read operations and requires injected errors to appear in operation output. Double restart builds a metamorphic DB, clones its FS, records golden KVs, then repeatedly opens/closes/reopens independent clones under random latency and checks KVs. Read-only recovery compares filesystem string state before and after open/close.

## State And Persistence Behavior
The tests stress persisted WAL, manifest, SSTable, blob/value-separation, and crash-clone state. Read-only recovery specifically asserts no filesystem mutation. Clone tests ensure option structs do not share mutable Pebble-owned fields after `Clone`.

## Dependencies And Integration Points
Uses package `pebble_test`, metamorphic workload generation, Cockroach key schema, bloom filters, value separation, `vfs`, `errorfs`, random latency, and public APIs. It validates external-user behavior rather than package internals.

## Risks And Edge Cases
Coverage includes silent read-error swallowing, WAL deletion before flush safety, large-batch recovery under small memtables, unsynced crash clones, read-only recovery side effects, and shallow-copy bugs in nested options.

## Test Signals
Signals include injected-error text in operation output, exact KV equality with a golden DB, unchanged FS state after read-only open, absence of restart data loss, and stable option string after mutating a clone.
