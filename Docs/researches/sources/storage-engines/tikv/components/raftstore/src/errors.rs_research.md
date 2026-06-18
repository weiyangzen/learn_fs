# sources/storage-engines/tikv/components/raftstore/src/errors.rs

Purpose: Defines raftstore's central `Error` enum, `Result` alias, transport discard reasons, conversion to client-facing `errorpb::Error`, and stable error-code classification. This is the boundary between internal raftstore failure modes and RPC-visible raft command errors.

Important APIs and types: `DiscardReason` distinguishes disconnected, filtered, paused, and full channels. `Error` includes leadership and region routing errors (`NotLeader`, `RegionNotFound`, `StoreNotMatch`, `KeyNotInRegion`), liveness/availability states (`ReadIndexNotReady`, `DataIsNotReady`, `RecoveryInProgress`, flashback states), persistence and dependency errors (`Io`, `Engine`, `Raft`, `Snapshot`, `Encryption`, `SstImporter`), and raftstore-specific conditions (`PendingPrepareMerge`, `IsWitness`, `MismatchPeerId`). `RAFTSTORE_IS_BUSY` is used for full transport queues.

Control flow: `From<Error> for errorpb::Error` always sets the text message, then fills structured protobuf sub-errors for recognized variants. Full transport queues map to `ServerIsBusy`; deadline exceeded uses `set_deadline_exceeded_busy_error`; coprocessor delay requests become `ServerIsBusy` with backoff. `From<TrySendError<T>>` maps channel full/disconnected into transport discard errors, and `From<DeadlineError>` maps directly to `DeadlineExceeded`.

State and persistence: This file has no storage behavior. Its state impact is semantic: the chosen error variant controls client retry behavior, leader redirection, stale epoch refresh, disk-full reporting, and whether callers see a generic message or structured protobuf field.

Dependencies and integration points: It depends on `kvproto::errorpb`, `metapb`, and `raft_serverpb` for wire errors, `error_code` for observability codes, engine/pd/raft/snapshot/import/encryption error types for conversion, and TiKV deadline helpers. It is re-exported from `lib.rs` and used across router, store, coprocessor, and command response helpers.

Risks: New `Error` variants must be added in three places to be fully useful: display text, protobuf conversion, and `ErrorCodeExt`. Missing protobuf mapping falls back to message-only errors. Some internal states such as `RegionNotRegistered` map to unknown, which is appropriate for internal diagnostics but weak for client logic. `Transport(Disconnected)` converts differently depending on path: `TrySendError` can become `Transport`, while router `handle_send_error` maps proposal disconnection to `RegionNotFound`.

Test signals: `test_deadline_exceeded_error` verifies that `DeadlineExceeded` becomes a server-busy style protobuf with the expected message and reason. Broader coverage is indirect through raftstore command response and routing tests.
