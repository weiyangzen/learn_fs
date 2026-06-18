# sources/user-network-fs/gcsfuse/internal/storage/gcs/errors.go

## Purpose
This file normalizes errors from Google storage clients into gcsfuse-specific semantic error types.

## Important APIs and Control Flow
`NotFoundError` wraps errors indicating a missing object name or generation. `PreconditionError` wraps failed preconditions. `GetGCSError` returns nil for nil input, maps `googleapi.Error` HTTP 404 to `NotFoundError`, HTTP 412 to `PreconditionError`, maps gRPC status `codes.NotFound` and `codes.FailedPrecondition`, maps `storage.ErrObjectNotExist` to `NotFoundError`, and otherwise returns the original error.

## State, Dependencies, and Integration
There is no state. Dependencies include `errors`, `fmt`, `net/http`, `cloud.google.com/go/storage`, `googleapi`, and gRPC status/codes. Storage implementations call `GetGCSError` so callers and tests can use `errors.As` or exact type expectations against local error classes instead of transport-specific errors.

## Risks and Test Signals
The function uses `errors.As` for `googleapi.Error` and `status.FromError` for gRPC statuses. Wrapped local `NotFoundError` or `PreconditionError` values are not specially unwrapped and may be returned unchanged or as their wrapper depending on the wrapping shape. Error classification affects retry, cache, and filesystem semantics, so missing a transport-specific error form can leak backend details upward.
