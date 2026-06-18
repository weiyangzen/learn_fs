# sources/storage-engines/foundationdb/fdbserver/include/fdbserver/fdbserver_stream_support.h

## Purpose
Defines Swift interop aliases for selected fdbserver Flow stream/request types around master and recovery RPCs.

## Important APIs, Types, and Functions
- `SWIFT_FUTURE_STREAM(TYPE)` creates `FutureStream_TYPE` and Swift continuation callback aliases.
- `SWIFT_REQUEST_STREAM(TYPE)` creates `RequestStream_TYPE` aliases.
- Aliases are generated for `UpdateRecoveryDataRequest`, `GetCommitVersionRequest`, `GetRawCommittedVersionRequest`, and `ReportRawCommittedVersionRequest`.

## Control Flow
No runtime control flow; inclusion exposes C++ Flow stream/request types in Swift-friendly alias form.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Includes Flow Swift compatibility headers, pthread/stdint, `MasterInterface.h`, and generated Swift C++ type conformances. Supports Swift/C++ interop for server stream types.

## Risks and Edge Cases
Macro-generated aliases depend on exact type names and generated Swift headers. Underlying request or conformance changes surface as build failures.

## Test Signals
Build success with Swift interop enabled is the primary signal.
