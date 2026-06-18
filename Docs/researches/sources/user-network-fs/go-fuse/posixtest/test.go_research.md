<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test.go -->
# sources/user-network-fs/go-fuse/posixtest/test.go

## Purpose
Defines the reusable POSIX filesystem conformance suite used by go-fuse filesystems and virtiofs tests.

## Important APIs, Types, and Functions
`All` maps names to tests covering symlinks, basic files, truncation, fd leaks, mkdir/rmdir, link/rename, deleted fstat, directory reads, append, openat, fallocate, locks, lseek holes, xattrs, and symlink races.

## Control Flow
Each test mutates a supplied mount/path with standard library and syscall operations, then checks observed POSIX semantics through stat, readback, errno, directory entries, locks, or xattr state.

## State and Persistence Behavior
State is limited to files under the supplied test root plus transient open fds and goroutines in race/parallel tests.

## Dependencies and Integration Points
Integrates with go-fuse filesystem tests, unionfs tests, virtiofs guest tests, `internal/xattr`, `internal/fallocate`, and platform flock helpers.

## Risks and Edge Cases
Several tests depend on kernel/filesystem support and may skip or fail on unsupported O_DIRECT, xattr, SEEK_HOLE, or lock behavior. `OpenSymlinkRace` is intentionally stressy.

## Test Signals
This file is the main behavior signal for filesystem correctness; running with `-race` and under real FUSE/virtiofs backends catches fd, locking, and path-resolution regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test.go -->
