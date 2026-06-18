<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/listfds.go -->
# sources/user-network-fs/go-fuse/posixtest/listfds.go

## Purpose
Lists open file descriptors for POSIX fd-leak tests, filtering known uninteresting descriptors.

## Important APIs, Types, and Functions
`listFds(pid, prefix)` returns strings of `fd[mode]=target` plus a filtered summary.

## Control Flow
It opens `/dev/fd` for the current process or `/proc/<pid>/fd` for another Linux process, reads entries, lstat/readlinks each fd, filters pipes, epoll, and non-prefix targets, and returns the rest.

## State and Persistence Behavior
No persistent state; it observes live process fd state and handles races where descriptors close mid-scan.

## Dependencies and Integration Points
Used by `posixtest.FdLeak`; depends on `/dev/fd`, Linux `/proc`, and Go runtime fd behavior.

## Risks and Edge Cases
Mode bits from fd symlinks are approximate, `/proc` is Linux-only for other pids, and filtering could hide relevant pipe leaks from splice-heavy code.

## Test Signals
`FdLeak` reads a file repeatedly and asserts the descriptor count remains low; race runs can catch descriptors closed during enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/listfds.go -->
