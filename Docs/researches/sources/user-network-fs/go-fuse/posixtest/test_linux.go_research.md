<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_linux.go -->
# sources/user-network-fs/go-fuse/posixtest/test_linux.go

## Purpose
Provides Linux-specific POSIX helpers and registers a Linux-only fallocate keep-size test.

## Important APIs, Types, and Functions
`sysFcntlFlockGetOFDLock` uses `unix.F_OFD_GETLK`; `FallocateKeepSize` validates `FALLOC_FL_KEEP_SIZE`; `init` adds it to `All`.

## Control Flow
The fallocate test writes data, allocates a range past the middle with keep-size, seeks back, reads all data, and verifies content is unchanged.

## State and Persistence Behavior
State is a single file under the supplied test root.

## Dependencies and Integration Points
Depends on Linux `unix` constants and `syscall.Fallocate`.

## Risks and Edge Cases
Filesystems without keep-size support may fail rather than skip; OFD lock behavior is Linux-specific.

## Test Signals
Linux `go test ./posixtest` exercises this through the `All` registry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_linux.go -->
