<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_freebsd.go -->
# sources/user-network-fs/go-fuse/posixtest/test_freebsd.go

## Purpose
Provides FreeBSD lock-query behavior for POSIX flock tests despite missing `F_OFD_GETLK`.

## Important APIs, Types, and Functions
`sysFcntlFlockGetOFDLock` creates a pipe, forks, queries `F_GETLK` in the child, writes the lock struct to the parent, and exits.

## Control Flow
The child uses a read-lock request to discover the write lock held by the parent process, approximating Linux OFD lock visibility.

## State and Persistence Behavior
Transient state includes forked child and pipe fds; the helper does not wait for the child explicitly.

## Dependencies and Integration Points
Used by `FcntlFlockSetLk` on FreeBSD; depends on raw `fork`, pipes, unsafe struct transfer, and `syscall.FcntlFlock`.

## Risks and Edge Cases
Missing wait can leave short-lived zombies; partial pipe reads are not checked; errors in the child are ignored.

## Test Signals
FreeBSD POSIX testing should run locking cases and watch for process leaks or hangs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_freebsd.go -->
