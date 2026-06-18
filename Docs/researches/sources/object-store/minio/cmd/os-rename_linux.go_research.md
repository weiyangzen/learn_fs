# sources/object-store/minio/cmd/os-rename_linux.go

## Purpose
This Linux-only file defines MinIO's low-level rename primitive for Linux.

## Important APIs, Types, and Functions
`RenameSys(src, dst string)` directly calls `syscall.Rename`.

## Control Flow and State
The function has no internal state or additional mapping. Higher-level error normalization is handled by `Rename` and `renameAll`.

## Dependencies and Integration Points
The file is selected by `//go:build linux`. `os-instrumented.go` calls `RenameSys` from the exported `Rename` wrapper, which records metrics and trace information.

## Risks and Test Signals
Direct syscall use preserves Linux errno behavior and avoids possible abstraction changes in `os.Rename`, but it also means Linux-specific behavior must be mapped correctly by higher layers. `os-reliable_test.go` exercises `renameAll` on the active platform.
