# sources/object-store/minio/cmd/os_unix.go

## Purpose
This file implements optimized Unix filesystem primitives for Linux, Darwin, and BSD builds. It avoids higher-level directory APIs for listing hot paths and adds direct fd opens with metrics.

## Important APIs, Types, and Functions
`access` uses `unix.Access`. `openFileWithFD` calls `syscall.Open` with `O_CLOEXEC` and records read/write fd metrics. `osMkdirAll` is a forked recursive mkdir that can skip work under `baseDir`. `parseDirEnt` parses raw `syscall.Dirent` records into names and file modes. `readDirFn` and `readDirWithOpts` use pooled buffers and `syscall.ReadDirent`; `globalSync` calls `syscall.Sync`.

## Control Flow and State
The listing loop reuses `direntPool` and `direntNamePool`, reads raw directory blocks, skips `.` and `..`, and falls back to `Stat` for unknown file types or symlinks. Symlinked directories are ignored unless `followDirSymlink` is set. Directory entries are returned with a slash suffix.

## Dependencies and Integration Points
The code depends on `internal/bpool`, platform helper functions such as `direntNamlen` and `direntInode`, MinIO path and error helpers, and OS metrics from `globalOSMetrics`.

## Risks and Test Signals
Unsafe dirent parsing is sensitive to struct layout and record length validation. The code must avoid leaking pooled buffers and must handle files disappearing during scans. `os-readdir_test.go` covers user-visible semantics; low-level parse errors depend on platform CI and filesystem diversity.
