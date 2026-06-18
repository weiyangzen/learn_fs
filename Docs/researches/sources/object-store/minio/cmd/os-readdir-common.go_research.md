# sources/object-store/minio/cmd/os-readdir-common.go

## Purpose
This small common file defines the shared API for MinIO directory listing helpers while leaving implementation to platform-specific files.

## Important APIs, Types, and Functions
`readDirOpts` carries `count` and `followDirSymlink`. `readDir` returns all entries by passing `count: -1`; `readDirN` returns at most `count` entries by forwarding to `readDirWithOpts`.

## Control Flow and State
There is no persistent state. The functions are simple adapters that normalize caller intent before dispatching to platform-specific `readDirWithOpts`.

## Dependencies and Integration Points
`readDirWithOpts` is implemented in `os_unix.go`, `os_windows.go`, and `os_other.go`. Callers elsewhere in MinIO get a stable API independent of `syscall.ReadDirent`, Windows `FindFirstFile`, or `os.File.Readdir`.

## Risks and Test Signals
Semantics such as symlink directory handling, count behavior, and trailing slash formatting depend on the selected platform implementation. `os-readdir_test.go` validates common behavior across empty directories, files, directories, symlinks, errors, and count limits.
