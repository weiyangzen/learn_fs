# File Research: sources/os/bsd/freebsd-src/sys/sys/syscallsubr.h

## Purpose
`syscallsubr.h` declares kernel-internal syscall helper routines used by syscall entry points and compatibility wrappers.

## Main Interfaces
- Declares `struct mmap_req` for normalized `mmap` requests and optional file-permission checking callback.
- Provides prototypes for process, signal, scheduler, socket, IPC, jail, capability, kqueue, AIO, timer, VM, and file-descriptor operations.
- VFS/filesystem-facing helpers include `kern_openat`, `kern_openatfp`, `kern_statat`, `kern_statfs`, `kern_fstatfs`, `kern_getfsstat`, `kern_getdirentries`, `kern_getfhat`, `kern_fhopen`, `kern_fhstat`, `kern_fhstatfs`, `kern_linkat`, `kern_renameat`, `kern_symlinkat`, `kern_readlinkat`, `kern_mkdirat`, `kern_mkfifoat`, `kern_mknodat`, `kern_funlinkat`, `kern_frmdirat`, `kern_ftruncate`, `kern_truncate`, `kern_fspacectl`, `kern_copy_file_range`, `kern_posix_fadvise`, and `kern_posix_fallocate`.
- Declares user cpuset copy helpers and legacy `freebsd11_kern_getdirentries`.

## Implementation Notes
The header centralizes normalized kernel entry points so syscall wrappers can handle ABI/user-copy details while shared logic lives in `kern_*` routines. Many parameters carry `enum uio_seg` to distinguish user and kernel address spaces.

## Dependencies and Constraints
Includes `sys/types.h`, cpuset/domainset/uio internals, MAC, mount, signal, and socket headers. Forward declarations keep the header broad but avoid pulling every subsystem definition.
