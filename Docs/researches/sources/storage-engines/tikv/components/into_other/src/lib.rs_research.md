# sources/storage-engines/tikv/components/into_other/src/lib.rs

## Purpose
This crate provides conversions between error types that cannot depend directly on one another. It is primarily an adapter from `engine_traits::Error` into protobuf PD/store errors and Raft storage errors.

## Important APIs, Types, and Functions
- `IntoOther<O>` is a local conversion trait with `into_other`.
- `impl IntoOther<ProtoError> for EngineTraitsError` creates a default `errorpb::Error`, stores the formatted message, and fills `key_not_in_region` fields for `EngineTraitsError::NotInRange`.
- `impl IntoOther<RaftError> for EngineTraitsError` wraps the engine error in `raft::StorageError::Other`.
- `into_other<F, T>` is a generic helper for callers that want function-style conversion.

## Control Flow
The conversion is a simple match on the consumed error. `NotInRange` gets structured protobuf fields; all other engine errors only produce a message.

## State and Persistence Behavior
No state is persisted. The source error is consumed.

## Dependencies and Integration Points
The file integrates `engine_traits`, `kvproto::errorpb`, and `raft`. It is useful at boundaries where storage errors must be sent to clients or returned through Raft APIs without creating direct dependencies in the original error crate.

## Risks
Only `NotInRange` preserves structured details in `ProtoError`; other variants lose type information except for the message. Because the conversion consumes the error, future code must not need to inspect it afterwards. Formatting-sensitive messages can become wire-visible.

## Test Signals
No local tests are present. Behavior is covered indirectly wherever engine errors are converted for raftstore or API responses.
