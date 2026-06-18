# sources/storage-engines/foundationdb/fdbctl/include/fdbctl/ControlCommands.h

## Purpose
This header declares the gRPC command-handler API and shared special-key constants for `fdbctl` when Flow gRPC support is enabled.

## Important APIs, Types, And Functions
It declares handlers for coordinators, configure, status, workers, include, exclude, exclude status, and kill. The `utils` namespace declares special-key error decoding and worker/storage/exclusion readers. The `special_keys` namespace defines coordinator, excluded/failed server, excluded/failed locality, force-option, in-progress-exclusion, and worker-interface verification keys/ranges.

## Control Flow
The header has no executable control flow. It defines the contract used by `ControlService.h` and implemented across `ControlCommands.cpp` and `ExcludeCommand.cpp`.

## State And Persistence Behavior
The constants identify FoundationDB special-key state that command handlers read and mutate. No local state is declared except function signatures.

## Dependencies And Integration Points
It includes FoundationDB client/storage interfaces, Flow gRPC support, and generated control-service protobuf/gRPC headers. It is the coupling point between generated RPC messages and Flow actor command implementations.

## Risks And Edge Cases
`configure` is declared but not implemented in the visible files and its handler is commented out in the service. Constants are duplicated with a TODO to point fdbcli code here, so drift with other management paths is possible.

## Test Signals
Compile/link tests with `FLOW_GRPC_ENABLED` should catch missing handler implementations. Behavioral tests should verify all special-key constants match the management API paths expected by FoundationDB.
