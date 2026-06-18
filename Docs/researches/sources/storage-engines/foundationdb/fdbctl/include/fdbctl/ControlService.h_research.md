# sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlService.h

## Purpose
This header adapts generated gRPC service methods to FoundationDB Flow actor handlers and ensures requests run on the main Flow thread with deadline handling.

## Important APIs, Types, And Functions
The `DEFINE_GRPC_HANDLER` macro defines synchronous gRPC overrides. Template `grpcHandlerWrapper` applies deadline-derived timeout handling and maps Flow errors to gRPC statuses. Class `ControlServiceImpl` derives from generated `fdbctl::ControlService::Service` and defines handlers for `GetCoordinators`, `ChangeCoordinators`, `GetStatus`, `GetWorkers`, `Include`, `Exclude`, `ExcludeStatus`, and `Kill`.

## Control Flow
Each gRPC method calls `handleRequestOnMainThread`, which schedules `grpcHandlerWrapper` through `onMainThread(...).getBlocking()`. The wrapper reads the gRPC deadline, uses `CLIENT_KNOBS->GRPC_CTL_SERVICE_DEFAULT_TIMEOUT` when no deadline is set, rejects expired deadlines, awaits the Flow handler under `timeoutError`, maps `timed_out` to `DEADLINE_EXCEEDED`, and maps other Flow errors to `INTERNAL`.

## State And Persistence Behavior
`ControlServiceImpl` stores a database reference. The wrapper itself is stateless; persistence occurs only in delegated command handlers.

## Dependencies And Integration Points
It depends on generated gRPC/protobuf code, `ControlCommands.h`, Flow thread helpers, generic actors, client knobs, and gRPC server contexts.

## Risks And Edge Cases
Deadline conversion truncates to whole seconds; sub-second deadlines can become zero and be rejected. Blocking on `getBlocking()` ties gRPC worker threads to Flow main-thread execution. Proto-declared RPCs `ConfigureAutoSuggest`, `Configure`, and `Maintenance` are not wired here, with `Configure` explicitly commented.

## Test Signals
Tests should cover deadline exceeded before execution, operation timeout, successful main-thread dispatch, internal error mapping, and reflection/registration showing only implemented RPCs are callable.
