# sources/user-network-fs/nfs-ganesha/src/include/os/linux/fsal_handle_syscalls.h

## Purpose
This Linux header abstracts by-handle and `*at` syscalls needed by FSAL/VFS code to operate on objects through persistent handles and special file descriptors.

## Important APIs, Types, And Control Flow
It defines missing `AT_EMPTY_PATH`, `O_PATH`, `AT_EACCESS`, `O_NOACCESS`, `F_OFD_GETLK`, `F_OFD_SETLK`, and `F_OFD_SETLKW` constants. When glibc has not exposed `MAX_HANDLE_SZ`, it defines `struct file_handle`, architecture-specific syscall numbers for aarch64, i386, x86_64, and PPC64, plus inline `name_to_handle_at` and `open_by_handle_at` wrappers around `syscall`. It also defines inline helpers `vfs_stat_by_handle`, `vfs_link_by_handle`, and `vfs_readlink_by_handle`.

## State And Persistence
There is no state in the header. Calls can create directory entries (`linkat`), open files by handle, or inspect handle-backed descriptors, so persistence is delegated to filesystem operations and kernel handle semantics.

## Dependencies And Integration Points
The header assumes `vfs_file_handle_t`, `struct stat`, and syscall prototypes are visible from surrounding includes. It is used by FSAL handle code that overlays Ganesha's handle representation with Linux `struct file_handle`.

## Risks And Test Signals
Architecture syscall-number drift, missing architecture definitions, and mount permission requirements for `open_by_handle_at` are key risks. Tests should cover handle lookup/open/stat/link/readlink on export filesystems, builds on each supported architecture, kernels with and without glibc declarations, and OFD lock constants in lock paths.
