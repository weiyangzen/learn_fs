# sources/storage-engines/tikv/components/compact-log-backup/src/errors.rs

## Purpose
Defines the compact-log-backup error wrapper, error categories, annotation helpers, and conversion utilities used across async compaction code.

## APIs and control flow
`Error` stores an `ErrorKind`, a notes string, and caller frames captured with `#[track_caller]`. `Display` prints the kind, optional note, and top caller location. `ErrorKind` wraps IO, protobuf, engine, codec, or uncategorized string failures. `From<T: Into<ErrorKind>> for Error` captures the current frame. `TraceResultExt` adds `trace_err` and `annotate` to crate `Result<T>`; these attach frames or replace notes before returning errors. `OtherErrExt::adapt_err` converts arbitrary displayable errors into `Other`. `Error::message` appends notes.

## State, dependencies, and integration
Errors are transient values but carry a stack-like vector of source locations for diagnostics. The module depends on `thiserror`, `tikv_util::codec`, `engine_traits`, protobuf, and `std::panic::Location`. Most compact-log-backup modules import `Result`, `TraceResultExt`, or `OtherErrExt`.

## Risks and test signals
`annotate` overwrites previous notes instead of appending through `message`, which may hide earlier context. Capturing static locations increases error size but improves traces. There are no direct tests here; coverage is indirect through modules that convert IO, protobuf, engine, codec, and generic errors.
