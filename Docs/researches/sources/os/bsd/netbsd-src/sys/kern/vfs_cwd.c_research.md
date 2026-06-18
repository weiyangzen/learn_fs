# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_cwd.c

## Purpose
Manages `struct cwdinfo`, the per-process/shareable current-directory state containing current directory, root directory, emulation root, umask, lock, and reference count.

## Main Interfaces
- `cwdinit`: allocate a new cwdinfo by copying the current process cwd/root/emulation-root vnodes and taking references.
- `cwdshare`: make another process share the current process cwdinfo.
- `cwdunshare`: ensure a process has a private cwdinfo when refcount is greater than one.
- `cwdfree`: drop a cwdinfo reference and release vnode references when the count reaches zero.
- `cwdexec`: unshare on exec and release the emulation-root vnode reference if present.

## State And Control Flow
`cwdinfo` is reference counted with atomic operations. Directory vnode pointers are protected by `cwdi_lock` during copying and are held with `vref`/released with `vrele`. `cwdunshare` copy-on-writes shared cwdinfo so updates after fork/exec do not affect other processes.

## Dependencies And Integration
Uses process `p_cwdi`, vnode references, rw locks, atomic refcounts, memory barriers, and kernel memory allocation.

## Risks And Edge Cases
- Correctness depends on callers holding or arranging appropriate process/cwd synchronization when changing `p_cwdi`.
- `cwdfree` uses release/acquire barriers around the final reference drop.
- `cwdexec` releases `cwdi_edir` if present; pointer clearing is not shown in this file, so surrounding exec code must treat this carefully.

## Filesystem Relevance
High. This is the per-process root/current-directory state used by path lookup, chroot behavior, and descriptor passing visibility checks.
