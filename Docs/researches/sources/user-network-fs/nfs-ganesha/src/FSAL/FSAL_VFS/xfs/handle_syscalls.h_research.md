# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.h

## Purpose

This header supplies the missing libhandle prototype for `fd_to_handle`, which the XFS syscall implementation needs but `xfs/handle.h` does not declare in this source version. The source was read as a complete 31-line file.

## Important APIs, Types, and Functions

It declares `int fd_to_handle(int fd, void **hanp, size_t *hlen);`.

## Control Flow

There is no runtime control flow. Including this header allows `handle_syscalls.c` to call `fd_to_handle` without relying on an implicit declaration.

## State and Persistence Behavior

No state is owned. The declared libhandle function allocates or returns handle storage through `hanp`/`hlen`, and callers free that storage with `free_handle`.

## Dependencies and Integration Points

The header belongs to the XFS FSAL build and complements `<xfs/handle.h>`. It is consumed by `handle_syscalls.c`.

## Risks and Edge Cases

Prototype drift against the installed libhandle ABI would cause compile or runtime linkage problems. The caller must preserve the allocation/free contract.

## Test Signals

Compile on distributions where `<xfs/handle.h>` lacks the prototype, link against libhandle, and exercise `vfs_fd_to_handle` so the declaration is validated at build and runtime.
