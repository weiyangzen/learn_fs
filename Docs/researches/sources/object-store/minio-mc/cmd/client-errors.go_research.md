# sources/object-store/minio-mc/cmd/client-errors.go

## Purpose

`client-errors.go` defines typed error values used across filesystem, S3, object, and stream operations.

## Important APIs, Types, and Functions

Error types include `APINotImplemented`, `InvalidArgument`, bucket errors, object errors, file path errors, symlink errors, `ObjectMissing`, `ObjectIsDeleteMarker`, `UnexpectedShortWrite`, `UnexpectedEOF`, `UnexpectedExcessRead`, and `SameFile`. Each implements `Error() string`.

## Control Flow

There is no branching beyond `ObjectMissing.Error`, which includes a time reference when present. The types are designed for `errors.As` or type switches, as seen in anonymous command handling.

## State and Persistence Behavior

No persistence. Error values carry contextual fields such as bucket, object, path, sizes, and time.

## Dependencies and Integration Points

These errors are used by client implementations and commands to provide typed failures and user-facing messages. `APINotImplemented` is explicitly handled by anonymous access commands; `UnexpectedEOF` is used by `catOut`.

## Risks and Edge Cases

Messages are user-visible API contracts for tests and scripts. `UnexpectedExcessRead` is a distinct type alias with its own text. Some comments contain old errno references but the code is platform-neutral.

## Test Signals

Tests should cover exact error strings, type assertions through `probe.Error`, time-specific object missing text, and stream size error formatting.
