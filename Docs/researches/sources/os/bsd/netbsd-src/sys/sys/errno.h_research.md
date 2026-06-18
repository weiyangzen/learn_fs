# File Research: sources/os/bsd/netbsd-src/sys/sys/errno.h

Read completely: 190 lines.

## Purpose
Defines NetBSD system error numbers, their stable numeric ABI values, compatibility aliases, and kernel-only pseudo-errors.

## Main Interfaces
- Standard errno constants: `EPERM` through `ENOTRECOVERABLE`.
- Alias: `EWOULDBLOCK` maps to `EAGAIN`.
- Limit marker: `ELAST` equals the largest errno value.
- Kernel/internal pseudo-errors under `_KERNEL || _KMEMUSER`: `EJUSTRETURN`, `ERESTART`, `EPASSTHROUGH`, `EDUPFD`, `EMOVEFD`.

## Dependencies And Integration
This header is a base ABI dependency for kernel and userland error reporting. VFS, file descriptor, ioctl, exec, networking, NFS, extended attributes, and synchronization code all use these symbolic return values.

## Risks And Edge Cases
- Numeric values are ABI-stable and must not be casually reordered.
- Kernel pseudo-errors are negative and are not user-visible errno values.
- `ELAST` must track the largest positive errno.

## Filesystem Relevance
High. Filesystem syscalls, vnode operations, mount code, NFS file handles, extended attributes, and device ioctls communicate failures through this namespace.
