# sources/object-store/minio/cmd/os-reliable.go

## Purpose
This file provides reliability wrappers around destructive and structural filesystem operations used by storage code: remove-all, mkdir-all, and rename. The wrappers normalize errors and retry a small set of races that occur when directories are concurrently created or deleted.

## Important APIs, Types, and Functions
`removeAll` validates arguments and path length, then calls `reliableRemoveAll`, which retries once on non-empty-directory errors. `mkdirAll` validates input, calls `reliableMkdirAll`, and maps not-directory/path-not-found cases to `errFileAccessDenied`. `reliableMkdirAll` retries once on `os.IsNotExist`, adjusting `baseDir` upward. `renameAll` validates source and destination, calls `reliableRename`, and maps cross-device, missing, exists, and access errors into MinIO object-layer errors.

## Control Flow and State
No persistent state is kept. The retry policy is deliberately narrow: one retry for known races, then return the mapped error.

## Dependencies and Integration Points
The code relies on wrapper functions from `os-instrumented.go`, path-length validation, MinIO error classifiers, and platform-specific `osMkdirAll` and `RenameSys`.

## Risks and Test Signals
Too-broad retrying could hide real disk failures, while too-narrow mapping could surface platform-specific syscalls to object APIs. `os-reliable_test.go` validates invalid arguments, long paths, successful mkdir/rename, and missing-source rename handling.
