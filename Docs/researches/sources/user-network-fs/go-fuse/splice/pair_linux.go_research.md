<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair_linux.go -->
# sources/user-network-fs/go-fuse/splice/pair_linux.go

## Purpose
Implements Linux-specific splice syscalls and pipe draining for `Pair`.

## Important APIs, Types, and Functions
`LoadFromAt`, `LoadFrom`, `WriteTo`, and `discard` are the important methods.

## Control Flow
Load methods splice from a file fd to the pair's write end; `WriteTo` splices from the read end to a destination fd; `discard` nonblocking-splices remaining bytes to `/dev/null` until `FIONREAD` reports empty.

## State and Persistence Behavior
No durable state beyond pipe contents; `discard` is called before returning a pair to the pool.

## Dependencies and Integration Points
Depends on Linux `syscall.Splice`, `/dev/null`, `unix.IoctlGetInt`, and pair capacity.

## Risks and Edge Cases
If an fd was accidentally closed, `discard` panics after trying to close both ends. `LoadFromAt` uses a local offset and does not advance the source fd.

## Test Signals
Splice tests cover over-capacity load and discard emptiness. Fault tests should simulate closed fds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair_linux.go -->
