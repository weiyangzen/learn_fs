# File Research: sources/os/bsd/freebsd-src/sys/sys/capsicum.h

## Purpose
`capsicum.h` defines FreeBSD Capsicum capability-mode rights, helper APIs, and kernel enforcement hooks.

## Main Interfaces
- `CAPRIGHT(idx, bit)` encodes a rights word with version/index metadata.
- Rights cover file I/O, seeking, mmap protections, creation/execution/fsync/truncate, lookup and `*at` operations, VFS metadata changes, sockets, MAC labels, semaphores, event/kqueue, ioctl, process descriptors, extattrs, ACLs, inotify, and grouped socket/kqueue rights.
- `CAP_ALL`, `CAP_NONE`, version/index helpers, fcntl masks, and `CAP_IOCTLS_ALL` support rights construction and limits.
- User/kernel common functions initialize, set, clear, validate, merge, remove, test, and compare rights.
- Kernel-only helpers include inline initializers, transient contains checks, `cap_check`, VM protection conversion, filedesc rights extraction, ioctl/fcntl checks, and capability-mode macros/tracing.
- Userland functions include `cap_enter`, `cap_sandboxed`, `cap_getmode`, descriptor rights/ioctl/fcntl limit and query APIs.

## Implementation Notes
Rights are split across indexed 64-bit words. Many compound rights intentionally include prerequisites such as `CAP_LOOKUP`, `CAP_READ`, `CAP_WRITE`, or `CAP_SEEK`. Kernel inline checks optimize the common success path and call failure reporting only when rights are missing.

## Dependencies and Constraints
Depends on `sys/param.h`, `sys/caprights.h`, `sys/file.h`, and `sys/fcntl.h`. Kernel currently statically asserts support for rights version 0 only.
