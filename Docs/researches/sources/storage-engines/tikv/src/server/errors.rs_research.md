# sources/storage-engines/tikv/src/server/errors.rs

## Purpose

This file defines the server-layer error envelope used by TiKV server components. It unifies IO, protobuf, gRPC, codec, raftstore, storage, engine, PD, HTTP, OpenSSL, worker scheduling, channel, and cluster-ID mismatch failures behind a single `Error` enum and `Result<T>` alias.

## Important APIs, Types, And Functions

- `Error` is a `thiserror::Error` enum with `#[from]` conversions for common subsystem errors.
- `Other(Box<dyn StdError + Sync + Send>)` carries arbitrary boxed errors.
- `SnapWorkerStopped(ScheduleError<SnapTask>)` represents snapshot-worker scheduling failure.
- `Sink`, `RecvError`, and `StreamDisconnect` model async/channel failures.
- `ClusterIDMisMatch { request_id, cluster_id }` reports request cluster ID mismatch explicitly.
- `pub type Result<T> = result::Result<T, Error>` is the local result contract.

## Control Flow

There is no runtime control flow beyond conversion and formatting. Call sites can use `?` to convert supported lower-level errors into `server::Error`, and error display/debug output is controlled by the enum variant annotations.

## State And Persistence Behavior

The file has no mutable state or persistence. It carries errors by value, including boxed dynamic errors for unsupported cases.

## Dependencies And Integration Points

It imports error types from `engine_traits`, `grpcio`, `hyper`, `openssl`, `pd_client`, `protobuf`, `raftstore`, `tikv_util`, `storage`, and the snapshot worker task type. It is a server boundary type rather than a storage-specific error type.

## Risks

- Several variants format with `{:?}` instead of user-facing display, which may produce verbose or unstable messages.
- `Other` erases structured error information.
- Adding new server tasks with schedule errors requires explicit variants if callers need automatic conversion.
- `ClusterIDMisMatch` is spelled with `MisMatch`, so renaming would be a compatibility churn point.

## Test Signals

No tests are defined in this file. Coverage is indirect through server paths that return `server::Result<T>` and use `?` on lower-level errors.
