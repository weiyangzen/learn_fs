# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/fsal_handle_syscalls.h

## Purpose
This FreeBSD FSAL handle syscall shim adapts Ganesha's VFS file-handle operations to FreeBSD's `fhlink`/`fhreadlink` and handle layout.

## Important APIs, Types, And Functions
It includes `fsal_convert.h`, `<sys/mount.h>`, and `syscalls.h`. It defines fallback constants for Linux-ish flags that FreeBSD may lack (`O_PATH`, `O_DIRECTORY`, `O_NOACCESS`, `AT_EMPTY_PATH`) and `HANDLE_DUMMY`. `struct v_fid` and `struct v_fhandle` model the FreeBSD handle data layout containing flags, filesystem id, and file id bytes. `v_to_fhandle(hdl)` converts a Ganesha handle data pointer to the `struct fhandle *` expected by FreeBSD calls. Inline wrappers are `vfs_stat_by_handle()`, `vfs_link_by_handle()`, and `vfs_readlink_by_handle()`.

## Control Flow
`vfs_stat_by_handle()` ignores missing FreeBSD `AT_EMPTY_PATH` semantics and calls `fstat()` on the mount file descriptor. `vfs_link_by_handle()` and `vfs_readlink_by_handle()` convert `fh->handle_data` to a native handle pointer and call `fhlink()` or `fhreadlink()`.

## State And Persistence
The header stores no state. The wrappers operate on descriptors, destination directories, names, buffers, and serialized handle bytes supplied by callers. Link creation can persist filesystem namespace changes through `fhlink()`.

## Dependencies And Integration Points
It integrates FreeBSD VFS FSAL code with common Ganesha handle abstractions (`vfs_file_handle_t`) and system calls declared in `syscalls.h`. It bridges source code written around Linux-style open/stat/link-by-handle APIs to FreeBSD primitives.

## Risks And Test Signals
Risks include handle layout/offset assumptions in `v_to_fhandle`, unused `srcfd`/`sname` parameters hiding semantic differences, fallback flag values changing behavior relative to Linux, and `fstat(mountfd)` not being equivalent to stat-by-handle for all callers. Test signals include FreeBSD compile tests, round trips for file handles from real mounts, hard-link-by-handle tests, symlink readlink-by-handle tests, and namespace/permission failure cases.
