# sources/user-network-fs/gcsfuse/internal/storage/gcs/errors_test.go

## Purpose
This file table-tests `GetGCSError` across nil, HTTP, gRPC, API error, storage sentinel, local error, and wrapped error cases.

## Important APIs and Control Flow
`TestGetGCSError` creates API errors from gRPC status values using `apierror.FromError`, constructs a matrix of input and expected errors, calls `GetGCSError`, and compares with `assert.Equal`. Cases include `googleapi.Error` 404/412/400, wrapped `googleapi.Error`, gRPC NotFound/FailedPrecondition/Internal, plain errors, wrapped gRPC NotFound, direct local `PreconditionError` and `NotFoundError`, wrapped local errors, `storage.ErrObjectNotExist`, API errors, and wrapped API errors.

## State, Dependencies, and Integration
There is no persistent state. Dependencies include `fmt`, `net/http`, `testing`, `storage`, `apierror`, `testify/assert`, `googleapi`, gRPC codes/status, and `errors`. The tests document exactly which wrapped forms are normalized and which are returned unchanged.

## Risks and Test Signals
The equality checks compare concrete error structs containing constructed error values; this is stricter than type-only assertions and can catch accidental wrapping differences. The TODO around wrapped gRPC status creation references an upstream issue, so this area may need updates when grpc-go behavior changes.
