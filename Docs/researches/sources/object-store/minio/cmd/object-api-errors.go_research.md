# sources/object-store/minio/cmd/object-api-errors.go

## Purpose
This file defines the object API error taxonomy and the conversion bridge from low-level storage/erasure errors into typed object-layer errors. Its central role is to keep backend storage failures, validation failures, replication failures, multipart failures, and S3-facing object state errors distinguishable to higher API layers.

## Important APIs, types, and functions
`toObjectErr` unwraps an incoming error with `unwrapAll`, preserves `context.Canceled`, and maps known storage sentinel errors into typed errors such as `BucketNotFound`, `BucketNotEmpty`, `BucketExists`, `StorageFull`, `SlowDown`, `PrefixAccessDenied`, `ObjectExistsAsDirectory`, `VersionNotFound`, `MethodNotAllowed`, `ObjectNotFound`, `InvalidUploadID`, `ObjectNameInvalid`, `ObjectTooLarge`, `ObjectTooSmall`, `InsufficientReadQuorum`, `InsufficientWriteQuorum`, and `IncompleteBody`. It accepts optional bucket/object/version/upload ID parameters and decodes directory-object names through `decodeDirObject`.

The file defines many error types with `Error()` methods: generic bucket/object errors backed by `GenericError`, quorum errors, object lock and conditional errors, bucket configuration errors, replication remote-target errors, lifecycle/transition errors, object-name errors, range errors, multipart errors, backend and unimplemented errors, metadata errors, replication permission errors, and data movement overwrite errors. Helper predicates include `isErrBucketNotFound`, `isErrReadQuorum`, `isErrWriteQuorum`, `isErrObjectNotFound`, `isErrVersionNotFound`, `isErrSignatureDoesNotMatch`, `isErrPreconditionFailed`, `isErrMethodNotAllowed`, `isErrInvalidRange`, `isReplicationPermissionCheck`, and `isDataMovementOverWriteErr`.

## Control flow
Most control flow is table-like dispatch in `toObjectErr`: after unwrapping, it switches on the underlying error string and constructs the higher-level error with as much contextual data as was passed. Error predicates use `errors.Is` for sentinel compatibility and `errors.As` for typed wrapper compatibility. Some types implement `Unwrap`, allowing callers to use Go error chains while still preserving object API context.

## State and persistence behavior
The file has no persistent state. Its state behavior is encoded in error values, especially bucket/object/version/upload fields and quorum reason fields. The correctness of these values matters because later HTTP translation, audit logging, replication, healing, and tests inspect the concrete type and rendered message.

## Dependencies and integration points
It depends on `context`, `errors`, `fmt`, and `io`, plus package-level sentinels from storage, erasure, typed error, and utility files. It is integrated broadly by object API implementations, HTTP error translation (`toAPIError` paths), tests that compare error messages or types, and replication/data movement code that needs specific classifications.

## Risks and test signals
The highest-risk area is string-based matching in `toObjectErr`; if a sentinel error message changes, conversion can silently fall through. Another risk is incomplete context in variadic parameters, producing typed errors with empty bucket/object fields. The helper predicates reduce risk by using `errors.Is` and `errors.As`, but some helpers still use direct type assertions and can miss wrapped values. Test signals are spread across object API tests that expect exact error strings/types for invalid buckets, missing objects, invalid upload IDs, invalid ranges, multipart failures, and quorum behavior.
