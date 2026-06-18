# sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceCorrectness.cpp

## Purpose
`SpecialKeySpaceCorrectnessWorkload` validates special key space read/write semantics, error handling, conflict range reporting, management commands, and metrics schemas. It creates test-only special key ranges, mirrors them through a RYW transaction, and compares direct special-key results to reference transaction results.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SpecialKeySpaceCorrectness`. Important methods include `_setup`, `testRywLifetime`, `getRangeCallActor`, `compareRangeResult`, `randomRWKeyRange`, `testSpecialKeySpaceErrors`, `testConflictRanges`, `managementApiCorrectnessActor`, and `metricsApiCorrectnessActor`. It uses `SpecialKeySpace`, `SKSCTestRWImpl`, `SKSCTestAsyncReadImpl`, `ReadYourWritesTransaction`, `FDBTransactionOptions::RAW_ACCESS`, `SPECIAL_KEY_SPACE_RELAXED`, `SPECIAL_KEY_SPACE_ENABLE_WRITES`, management API command prefixes, JSON schemas, and system keys.

## Control Flow
Setup creates a fresh `SpecialKeySpace`, configures a RYW transaction at version 100, registers random test-only read/write or async-read ranges, and populates random keys. `start` runs a lifetime cancellation test, then concurrently runs special-key error tests, randomized getRange comparison, read and write conflict range comparison, and metrics schema validation for `testDuration`. Client 0 additionally runs management API correctness that changes coordinators when possible, verifies maintenance and data-distribution special keys, disables/re-enables DD-related settings, and checks underlying system keys.

## State And Persistence Behavior
Most test-only special-key state is in a local RYW transaction and `SpecialKeySpace` module implementations. Management API tests can durably change coordinators, maintenance/DD mode, healthy-zone, rebalance ignore state, and then restore/clear those changes. Conflict range tests manipulate transaction conflict metadata exposed through special keys.

## Dependencies And Integration Points
It depends on global config, ManagementAPI, NativeAPI, ReadYourWrites, Schemas, SpecialKeySpace modules, server knobs, tester interfaces, and system data ranges. It disables all failure injection workloads because cluster health and configuration stability are prerequisites for deterministic management API validation.

## Risks And Edge Cases
The workload intentionally covers many tricky boundary conditions: cross-module reads, relaxed reads, no-module errors, selector clamping, special-key write-disabled errors, cross-module clears, legal range bounds, RYW-disabled conflict range behavior, committed write conflict range reads, and worker interface reads. Management tests can alter real cluster configuration and must reliably revert coordinator and DD changes.

## Test Signals
`wrongResults` must remain zero for `check` to pass. Failures emit `TestFailure` details for range flag/size/key/value mismatches, conflict range mismatches, out-of-order results, schema failures, and unexpected management API responses. Metrics schema validation uses `schemaMatch` against `faultToleranceStatusSchema`.
