# sources/object-store/minio/cmd/os_windows.go

## Purpose
This Windows-only file implements access, mkdir-all, directory listing, and sync stubs using Windows filesystem APIs.

## Important APIs, Types, and Functions
`access` uses `os.Lstat`. `osMkdirAll` delegates to `os.MkdirAll`. `readDirFn` and `readDirWithOpts` use `syscall.FindFirstFile` and `FindNextFile` over `filepath.Clean(dirPath) + "\\*"`. `syscallErrToFileErr` maps Windows errors into MinIO file errors. `globalSync` is a no-op.

## Control Flow and State
The directory loops skip empty, `.` and `..` entries. Reparse points are treated as symlinks and resolved with `os.Stat`; symlinked directories are skipped unless explicitly followed in `readDirWithOpts`. Directory entries receive MinIO's slash separator.

## Dependencies and Integration Points
The implementation satisfies the common `readDirWithOpts`, `readDirFn`, `access`, and `osMkdirAll` contracts used by higher-level OS wrappers.

## Risks and Test Signals
Windows error mapping differs from Unix and can conflate missing paths with not-directory cases, which higher-level code explicitly accounts for. Symlink behavior depends on privileges. Shared read-directory tests skip symlink coverage on Windows but still validate listing and count behavior.
