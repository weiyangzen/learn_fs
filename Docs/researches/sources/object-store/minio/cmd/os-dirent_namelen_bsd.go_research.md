# sources/object-store/minio/cmd/os-dirent_namelen_bsd.go

## Purpose
This platform-specific helper returns the directory-entry name length on Darwin and BSD systems where `syscall.Dirent` exposes `Namlen`.

## Important APIs, Types, and Functions
- Build tags: `darwin || freebsd || openbsd || netbsd`.
- `direntNamlen(dirent *syscall.Dirent) (uint64, error)` returns `uint64(dirent.Namlen), nil`.

## Control Flow
The function performs a direct field read and always returns nil error.

## State and Persistence Behavior
The function is pure and does not mutate global or filesystem state.

## Dependencies and Integration Points
It depends on `syscall` and complements `os-dirent_namelen_linux.go`, which must derive name length from the name buffer. Higher-level directory scanning can call `direntNamlen` uniformly across operating systems.

## Risks and Edge Cases
Build tags must match platforms where `Dirent.Namlen` exists. Nil input would panic. Since it trusts the kernel-provided `Namlen`, malformed entries are not independently checked here.

## Test Signals
No direct tests are present. Platform compilation and directory scanning behavior are the primary signals.
