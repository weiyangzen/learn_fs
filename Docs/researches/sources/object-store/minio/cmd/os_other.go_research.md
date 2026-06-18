# sources/object-store/minio/cmd/os_other.go

## Purpose
This Plan 9 and Solaris implementation supplies access, mkdir-all, directory iteration, directory listing, and global sync behavior for platforms that do not use the Unix `ReadDirent` fast path or Windows APIs.

## Important APIs, Types, and Functions
`access` uses `os.Lstat`. `osMkdirAll` delegates to `os.MkdirAll` and ignores `baseDir`. `readDirFn` opens a directory with instrumented `Open`, reads batches through `Readdir`, filters symlinked directories, and invokes a callback. `readDirWithOpts` returns regular files and slash-suffixed directories with optional count limiting and symlink directory following. `globalSync` records sync metrics and calls `syscall.Sync`.

## Control Flow and State
Directory reads process up to 1000 entries per batch. Missing directories are treated as no-op for `readDirFn` but as errors for `readDirWithOpts`. Symlinks are resolved with `Stat`; disappearing targets and too-many-symlink conditions are skipped.

## Dependencies and Integration Points
This file implements the common APIs consumed by `os-readdir-common.go` and `os-instrumented.go`. It depends on MinIO error mappers and slash constants.

## Risks and Test Signals
The implementation is simpler but may be slower than the Unix `ReadDirent` version. `readDirN` count limiting slices filesystem batches before filtering, so symlink skips can reduce returned counts. Shared readdir tests provide semantic coverage where these platforms are tested.
