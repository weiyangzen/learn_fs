# sources/storage-engines/tikv/components/backup-stream/src/errors.rs

## Purpose
`errors.rs` defines the backup stream error model, error-code mapping, contextual wrapping helpers, reporting helpers, and a small annotation macro used throughout the backup-stream crate.

## Important APIs, types, and functions
- `Error` covers logical backup-stream states (`NoSuchTask`, `ObserveCanceled`, `MalformedMetadata`, `OutOfQuota`) and wrapped subsystem failures from gRPC, protobuf, IO, TiKV transaction code, scheduler, PD, raftstore, encryption, and boxed miscellaneous errors.
- `impl ErrorCodeExt for Error` maps each variant to `error_code::backup_stream::*` codes, preserving the inner code for `Contextual`.
- `ContextualResultExt` adds eager and lazy context wrapping to `Result<T, E> where E: Into<Error>`.
- `ReportableResult` logs `Result<(), E>` failures through `Error::report`.
- `annotate!` converts arbitrary errors into `Error::Other` with formatted context.
- `Error::report`, `report_fatal`, `without_context`, and `context` centralize logging and metrics updates.

## Control flow
Most modules construct ordinary `Result<T, Error>` values. Callers add context near subsystem boundaries and call `report` or `report_if_err` when the error should be logged but not returned. Fatal endpoint paths call `report_fatal` before pausing tasks and writing metadata. `without_context` lets retry logic inspect the root cause, for example initial scan retry behavior.

## State and persistence behavior
The file has no durable state. Its side effects are logging and Prometheus counters: `STREAM_ERROR` and `STREAM_FATAL_ERROR` are incremented with the mapped error kind.

## Dependencies and integration points
It depends on subsystem error types from encryption, grpcio, PD client, protobuf, raftstore, TiKV transaction code, and worker scheduling. It also imports `Task` because `ScheduleError<Task>` is a concrete variant.

## Risks and edge cases
- `Error::Other` erases structured classification except for the generic `OTHER` code.
- The `annotate!` macro boxes string-formatted errors, so callers lose downcastable root types.
- `ReportableResult` only handles unit results; non-unit values still need explicit handling.
- Context strings can be constructed eagerly unless `context_with` is used.

## Test signals
Tests validate contextual formatting and error-code preservation. Benchmarks compare context construction costs for direct formatting, `format_args!`, lazy closure context, baseline error handling, and successful contextual calls.
