# sources/storage-engines/foundationdb/flow/include/flow/error_definitions.h

## Purpose
Central X-macro list of FoundationDB error names, numeric codes, and messages for generating factories, enums, mappings, and bindings.

## Important APIs, Types, And Functions
The API is the `ERROR(name, code, message)` stream. Groups include normal operational failures, platform errors, client/API errors, backup/restore/task errors, snapshot/encryption errors, internal errors, authorization errors, and gRPC.

## Control Flow
Consumers define `ERROR`, include the file, expand every entry, and the header undefines `ERROR`. Removed-code comments preserve compatibility gaps.

## State And Persistence Behavior
Numeric codes are durable API/protocol semantics crossing clients, logs, RPC, and sometimes persisted metadata. Messages and names support diagnostics and generated bindings.

## Dependencies And Integration Points
Integrated with `flow/Error.h`, retry logic, bindings, RPC serialization, simulation, storage engines, backup/restore, encryption, special keys, and tooling.

## Risks And Edge Cases
Renumbering or reusing codes breaks compatibility. The file warns to add specific errors only when code can react specifically. Some errors are dangerous to catch because handling can delete server data.

## Test Signals
Generated mappings, factory functions, binding exposure, retryability classes, serialization, and behavior for conflict/timeout/maybe-delivered/auth/storage/backup errors.
