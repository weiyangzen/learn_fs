# sources/object-store/minio/cmd/os-rename_nolinux.go

## Purpose
This non-Linux file supplies the portable rename primitive for all non-Linux builds.

## Important APIs, Types, and Functions
`RenameSys(src, dst string)` delegates to `os.Rename`.

## Control Flow and State
There is no state. The function delegates all behavior to the Go runtime and OS implementation.

## Dependencies and Integration Points
The build tag `!linux` excludes this file on Linux. It is called by `Rename` in `os-instrumented.go` and then normalized by higher-level reliable wrappers.

## Risks and Test Signals
Different operating systems return different errors for missing parents, destination directories, and permission failures; those are handled in `os-reliable.go`. Shared reliable rename tests provide partial coverage, but platform-specific edge cases remain dependent on CI coverage per OS.
