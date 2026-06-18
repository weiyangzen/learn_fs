# sources/object-store/minio/cmd/os-dirent_fileino.go

## Purpose
This platform-specific helper returns an inode-like identifier from `syscall.Dirent` on BSD platforms where the field is named `Fileno`.

## Important APIs, Types, and Functions
- Build tags: `freebsd || openbsd || netbsd`.
- `direntInode(dirent *syscall.Dirent) uint64` returns `uint64(dirent.Fileno)`.

## Control Flow
There is no branching. Callers pass a directory entry and receive the platform's file number as a `uint64`.

## State and Persistence Behavior
The function is pure and reads only the supplied `syscall.Dirent`. It does not mutate state or persist data.

## Dependencies and Integration Points
It depends on Go's `syscall` package and complements `os-dirent_ino.go`, which provides the same function for Linux/Darwin. Higher-level directory walking code can call `direntInode` without build-time field-name conditionals.

## Risks and Edge Cases
The main risk is build-tag coverage: this file must compile only on platforms where `Dirent.Fileno` exists. Null `dirent` would panic, so callers must pass valid entries.

## Test Signals
No direct tests are present in this file. Coverage is expected through platform builds and any directory traversal tests that compile and call `direntInode`.
