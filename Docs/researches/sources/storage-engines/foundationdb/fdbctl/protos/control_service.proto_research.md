# sources/storage-engines/foundationdb/fdbctl/protos/control_service.proto

## Purpose
This proto defines the public gRPC API for `fdbctl` cluster control operations, including coordinator changes, configuration, status, worker listing, include/exclude, kill, and maintenance.

## Important APIs, Types, And Functions
The `ControlService` service declares RPCs `GetCoordinators`, `ChangeCoordinators`, `ConfigureAutoSuggest`, `Configure`, `GetStatus`, `GetWorkers`, `Include`, `Exclude`, `ExcludeStatus`, `Kill`, and `Maintenance`. Message types include `Worker`, coordinator request/reply types, `ConfigureRequest/Reply`, `GetStatusReply`, `IncludeRequest/Reply`, `ExcludeRequest/Reply`, `ExcludeStatusReply`, `KillRequest/Reply`, and `MaintenanceRequest/Reply`.

## Control Flow
The proto has no executable flow, but it defines request/response contracts used by generated C++ and other language bindings. Enums encode configuration choices such as redundancy mode, storage engine, storage migration type, configure result, and maintenance operation/result.

## State And Persistence Behavior
Messages model cluster state and desired mutations. Actual persistence is in FoundationDB special keys and management APIs implemented by server handlers.

## Dependencies And Integration Points
It sets Go and Java package options and is consumed by CMake `generate_grpc_protobuf`. The generated C++ headers are included by fdbctl service/command code.

## Risks And Edge Cases
The proto surface is ahead of current C++ service wiring: configure autosuggest, configure, maintenance, exclude `hosts`, exclude `all`, include `localities`, include reply counts, and kill duration are not fully implemented in the observed handlers. Proto3 `optional` fields require generated-code support compatible with the toolchain.

## Test Signals
Signals include generated-code compilation, gRPC reflection/contract tests, request compatibility across Go/Java/C++, and end-to-end tests proving every declared field either works or is explicitly rejected.
