# sources/storage-engines/foundationdb/fdbserver/workloads/ChangeConfig.cpp

## Purpose
`ChangeConfig.cpp` defines the `ChangeConfig` workload. It waits for a configurable delay, then changes the database configuration and/or coordinator set, including simulated extra databases. It specifically exercises management API configuration strings and special-key coordinator commands, including auto-coordinator discovery and error-schema validation.

## Important APIs, Types, And Functions
The core type is `ChangeConfigWorkload : TestWorkload`, with helpers `getConfigMode`, `configureExtraDatabase`, `configureExtraDatabases`, `changeConfigClient`, and `coordinatorsChangeActor`. It uses `ManagementAPI::changeConfig`, `waitForFullReplication`, simulated extra database creation, `SpecialKeySpace`, `JSONSchemas::managementApiErrorSchema`, `schemaMatch`, and `ReadYourWritesTransaction`.

## Control Flow
Only client 0 runs. After a random delay in `[minDelayBeforeChange, maxDelayBeforeChange]`, `changeConfigClient` may configure extra databases first or last. For the main database, it optionally applies `startingDisabledConfiguration` in simulation, waits for full replication, strips `"new "` from config modes when applying to an existing DB, and calls `changeConfig`. If coordinator changes are requested, it runs one or more `coordinatorsChangeActor` iterations, with repeated changes only for `"auto"`.

## State And Persistence
Persistent state includes cluster configuration changes, coordinator connection-string changes, and extra database configuration/coordinator state in simulation. The coordinator actor writes management special keys and expects the management special-key API to report command completion/failure through the error message module.

## Dependencies And Integration Points
The workload depends on the management API, special-key management modules, schema validation, `fdbrpc/simulator.h`, simulation policy extra databases, and tester workload failure-injection controls. It disables all failure-injection workloads because cluster configuration and coordinator changes are intentionally disruptive.

## Risks
Coordinator special-key writes are expected to throw `special_keys_api_failure`; the code asserts after a successful commit, so behavior changes in the API contract would fail the workload. Auto-coordinator selection can initially fail with retriable errors and only retries a bounded path. Misconfigured network addresses or insufficient machines can make the management API return schema-validated failures rather than apply changes. Extra database configuration is simulation-only and may race with main database changes.

## Test Signals
Trace events include `WaitForReplicas`, `WaitForReplicasExtra`, `GetAutoCoordinatorsChange`, `CoordinatorsChangeBeforeCommit`, and `CoordinatorsChangeError`. The workload `check` returns true, so failures are via assertions, thrown management errors, or schema mismatches.
