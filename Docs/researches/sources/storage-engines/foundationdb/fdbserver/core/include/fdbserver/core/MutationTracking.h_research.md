# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MutationTracking.h

## Purpose
This header declares optional debug tracing helpers for targeted mutation and key-range tracking in simulation/debug builds.

## Important APIs, Types, And Functions
`MUTATION_TRACKING_ENABLED` currently defaults to `0`. Macros `DEBUG_MUTATION`, `DEBUG_KEY_RANGE`, and `DEBUG_TAGS_AND_MESSAGE` short-circuit calls to `debugMutation`, `debugKeyRange`, and `debugTagsAndMessage`, which return `TraceEvent` objects.

## Control Flow
When enabled, call sites can emit trace events for mutations, key ranges, or tagged commit blobs. The comments note that range/tag helpers log only the first occurrence of a tracked key.

## State And Persistence Behavior
There is no durable state. The tracked-key set is defined in the implementation file to reduce recompilation, and output is trace logging only.

## Dependencies And Integration Points
It depends on FDB types, commit transaction structures, and Flow tracing. Integration points are mutation handling, commit proxy/TLog/storage paths, and simulation debugging.

## Risks And Edge Cases
Because the macros use boolean short-circuiting with `TraceEvent` expressions, enabling tracking can affect compile-time and runtime behavior if misused. Logging only first occurrences can hide repeated corruption patterns.

## Test Signals
Test signals are mostly diagnostic: compile with tracking enabled, confirm targeted events appear for selected keys, and verify disabled builds do not emit or pay meaningful overhead.
