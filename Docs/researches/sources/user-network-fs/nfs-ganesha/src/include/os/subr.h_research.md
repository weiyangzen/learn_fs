# sources/user-network-fs/nfs-ganesha/src/include/os/subr.h

## Purpose
This OS subroutine header defines common file timestamp, directory-entry, and credential helper interfaces used by Ganesha's portable VFS layer.

## Important APIs, Types, And Control Flow
It defines fallback `UTIME_NOW` and `UTIME_OMIT`, declares `vfs_utimesat`, `vfs_utimes`, `vfs_readents`, `to_vfs_dirent`, `setuser`, `setgroup`, and `set_threadgroups`, and defines `getuser`/`getgroup` aliases to `geteuid`/`getegid`. `struct vfs_dirent` normalizes inode, record length, type, offset, and name fields.

## State And Persistence
The header itself has no state. Implementations change file timestamps, parse directory buffers, and mutate effective user/group/thread group credentials.

## Dependencies And Integration Points
It includes `<stdbool.h>`, `<extended_types.h>`, and `<unistd.h>`. FSAL and protocol code use it to avoid platform-specific directory-entry and credential switching details.

## Risks And Test Signals
Credential-changing helpers are security-sensitive and thread-affinity matters. Directory parsing can be ABI-sensitive across OSes. Tests should cover timestamp special values, directory iteration across file types, privilege drop/restore behavior, supplementary group application, and concurrent request handling under credential changes.
