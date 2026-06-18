# sources/user-network-fs/nfs-ganesha/src/include/os/darwin/sys_resource.h

## Purpose
This Darwin portability header declares a platform wrapper for retrieving the open-file resource limit.

## Important APIs, Types, And Functions
It includes `<sys/resource.h>` and declares `int get_open_file_limit(struct rlimit *rlim);`.

## Control Flow
Callers pass an `rlimit` pointer to the wrapper. The implementation outside this header is expected to perform the Darwin-appropriate `RLIMIT_NOFILE` query and return a normal system-call style status.

## State And Persistence
No state is stored in the header. The function writes into caller-provided `struct rlimit` memory and reads process/kernel resource-limit state.

## Dependencies And Integration Points
It integrates generic resource-limit code with Darwin-specific implementation. It is paired with FreeBSD's macro version and likely a Linux equivalent so common code can call `get_open_file_limit()`.

## Risks And Test Signals
Risks are implementation/header mismatch, null `rlim` handling, and platform differences in maximum file descriptor limits. Test signals include Darwin compile tests and runtime checks comparing the wrapper result to `getrlimit(RLIMIT_NOFILE, ...)`.
