# sources/object-store/minio-mc/cmd/admin-service-unfreeze.go

## Purpose

`admin-service-unfreeze.go` implements `mc admin service unfreeze`, which resumes S3 API calls on a MinIO cluster after a freeze operation.

## Important APIs, Types, and Functions

`adminServiceUnfreezeCmd` defines the CLI command. `serviceUnfreezeCommand` is the output message type. `checkAdminServiceUnfreezeSyntax` enforces one target, and `mainAdminServiceUnfreeze` performs the admin operation.

## Control Flow

The command validates the target, builds an admin client, creates a cancellable context, calls `ServiceUnfreezeV2`, falls back to deprecated `ServiceUnfreeze` on error, converts the final error through `probe`, and prints a success message.

## State and Persistence Behavior

No local files are written. Remote server state is changed by unfreezing service calls. The only runtime state is the cancellable context and message payload.

## Dependencies and Integration Points

It depends on `newAdminClient`, `madmin-go` unfreeze APIs, `globalContext`, command registration in `admin-service.go`, and shared console/message helpers.

## Risks and Edge Cases

The fallback is unconditional on any V2 error, so non-version failures may trigger a second request. Correctness depends on server-side idempotence for unfreeze. There is no wait/verification path after sending the command.

## Test Signals

Tests should exercise exact arity, V2 success, V2 failure with legacy fallback, final error reporting, and text/JSON output content.
