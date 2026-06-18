# sources/storage-engines/foundationdb/fdbctl/ControlCommands.cpp

## Purpose
This file implements several gRPC-backed administrative commands for `fdbctl` when Flow gRPC is enabled. It covers coordinators, status, workers, include, kill, and shared utility reads from management/system special keys.

## Important APIs, Types, And Functions
Top-level handlers include `getCoordinators`, `changeCoordinators`, `getStatus`, `getWorkers`, `include`, and `kill`. Helpers include `getTransaction`, `localityDataToProto`, `addInterfacesFromKVs`, `getWorkerInterfaces`, `utils::getSpecialKeysFailureErrorMessage`, `utils::getStorageServerInterfaces`, and `utils::getWorkersProcessData`.

## Control Flow
Handlers create transactions, set required special/system key options, run reads/writes through `ThreadFuture` bridged by `safeThreadFutureToFuture`, and retry through `tr->onError`. Coordinator change writes special keys and expects commit to fail with `commit_unknown_result`; special-key failure messages are inspected to distinguish not-enough-machines and same-address results. Worker listing reads process classes and worker list keys, merges class data, filters tester processes, and writes `Worker` protos. `kill` resolves worker interfaces and calls `db->rebootWorker` for all or selected addresses.

## State And Persistence Behavior
Read-only operations fetch special/system key state. Mutating operations write special keys for coordinator changes and inclusion, or send reboot requests to workers. No local persistence is used.

## Dependencies And Integration Points
It depends on FoundationDB management APIs, special key ranges, worker/process metadata encoders, Flow actors/futures, gRPC statuses, Boost string splitting/joining, JSON schema validation, and generated `control_service` protos.

## Risks And Edge Cases
This code is compiled only with `FLOW_GRPC_ENABLED`. Some requests are partially implemented: `kill` ignores `duration_seconds`, and `include` parses only `addresses` while declaring but never populating `localities`. Several failure paths use `ASSERT`, which is unsuitable for graceful API errors if cluster state is malformed. `changeCoordinators` has a TODO to reject disjoint coordinator sets.

## Test Signals
Useful tests issue gRPC requests against a test cluster for coordinator get/change, status JSON retrieval, worker listing, include all/specific, invalid address parsing, unknown kill targets, and special-key failure translation.
