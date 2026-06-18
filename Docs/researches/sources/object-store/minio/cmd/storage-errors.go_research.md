# sources/object-store/minio/cmd/storage-errors.go

## Purpose

`storage-errors.go` centralizes storage-layer sentinel errors and maps low-level operating-system errors into MinIO storage errors. It gives disk, volume, file, bitrot, versioning, and backend failure paths stable error values that higher layers can classify and translate into object-layer or S3 API behavior.

## Important APIs, Types, And Functions

The file defines many package-level sentinels as `StorageErr`, including disk state errors (`errDiskNotFound`, `errFaultyDisk`, `errFaultyRemoteDisk`, `errDiskFull`, `errDiskAccessDenied`, `errUnsupportedDisk`, `errDriveIsRoot`), format/backend errors (`errCorruptedFormat`, `errCorruptedBackend`, `errUnformattedDisk`, `errInconsistentDisk`, `errXLBackend`), file and volume errors (`errFileNotFound`, `errFileVersionNotFound`, `errFileAccessDenied`, `errFileCorrupt`, `errPathNotFound`, `errVolumeNotFound`, `errVolumeExists`, `errVolumeNotEmpty`, `errVolumeAccessDenied`), and protocol/data errors (`errLessData`, `errMoreData`, `errBitrotHashAlgoInvalid`, `errMaxVersionsExceeded`).

It also defines plain `errors.New` control-flow sentinels: `errDoneForNow`, `errSkipFile`, and `errIgnoreFileContrib`. `baseErrs` contains common disk-unavailable errors, and `baseIgnoredErrs` currently aliases that slice.

`type StorageErr string` implements `Error() string`, making the sentinel value itself the message and keeping comparisons simple when callers hold the exact package variable.

`osErrToFileErr(err error) error` is the main function. It returns nil for nil input, maps not-exist, permission, not-directory/is-directory, path-not-found, too-many-files, invalid-handle, I/O, invalid-argument, and no-space conditions to storage sentinels, and returns unknown errors unchanged.

## Control Flow

`osErrToFileErr` is a prioritized classification chain. It first handles nil, then common object/file lookup failures, permission failures, path shape errors, file descriptor exhaustion, invalid handles, disk I/O failures, invalid arguments, and disk-full conditions. Invalid-argument errors are logged through `storageLogIf(context.Background(), err)` before returning `errFileNotFound`; the comment explains this is intended for odd `O_DIRECT` read behavior on some filesystems.

## State And Persistence Behavior

The file does not mutate storage state. Its sentinels shape persistence behavior indirectly by guiding callers: disk full prevents writes, not-found drives read/list/delete responses, faulty disk errors affect erasure set availability, and cross-device rename errors point to backend misconfiguration that can break atomic rename assumptions.

Because `StorageErr` values are strings, error text is part of the observable behavior. Changing messages can affect logs, tests, admin tooling, and any code comparing error strings instead of sentinel identity.

## Dependencies And Integration Points

The file imports `context` and `errors`. It depends on OS helper predicates declared elsewhere in the package, including `osIsNotExist`, `osIsPermission`, `isSysErrNotDir`, `isSysErrIsDir`, `isSysErrPathNotFound`, `isSysErrTooManyFiles`, `isSysErrHandleInvalid`, `isSysErrIO`, `isSysErrInvalidArg`, and `isSysErrNoSpace`. It also integrates with `storageLogIf` for unexpected invalid-argument logging.

Storage implementations, erasure code, REST handlers, healing, scanners, and object-layer translation code consume these sentinels to decide whether an operation is retryable, ignorable, fatal, or user-visible.

## Risks

Misclassification can cause serious behavior changes. Mapping an I/O error to not-found would hide disk corruption; mapping not-found to faulty disk would reduce availability; changing `errCrossDeviceLink` behavior could mask non-atomic backend renames. The alias `baseIgnoredErrs = baseErrs` means in-place mutation of either slice would affect the other.

The invalid-argument path deliberately maps to `errFileNotFound`, which is pragmatic for `O_DIRECT` edge cases but can hide other EINVAL causes after logging. Callers that wrap errors without preserving sentinel identity may also weaken classification.

## Test Signals

This file has no direct tests in the requested set. Useful coverage should include table tests for `osErrToFileErr` using representative `os.PathError` and platform-specific syscall errors, plus integration tests that ensure storage REST and object-layer code translate these sentinels to expected API errors.
