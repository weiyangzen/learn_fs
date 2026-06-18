# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_uio.c

## Purpose
Implements common `uio`/`iovec` movement helpers and related user/kernel copy utilities. This is central to read/write paths, including VFS and filesystem code.

## Copy Helpers
- `copyin_nofault()` and `copyout_nofault()` disable page faults around `copyin()`/`copyout()`.
- `physcopyin()` and `physcopyout()` build a one-element `uio` and use `uiomove_fromphys()` to copy to/from physical pages.
- `physcopyin_vlist()` and `physcopyout_vlist()` copy through bus DMA segment lists with offsets.

## `uiomove`
- `uiomove()` copies between kernel buffer and `uio`, allowing faults.
- `uiomove_nofault()` performs the same operation with nofault behavior.
- `uiomove_faultflag()` handles the core loop:
  - validates direction, segment type, current thread for userspace `uio`, and nonnegative residual;
  - sets thread flags for deadlock treatment and optional nofault behavior;
  - iterates iovecs, skips empty entries, caps copy size, and updates base/length/residual/offset;
  - handles `UIO_USERSPACE` via `copyin`/`copyout`, `UIO_SYSSPACE` via `bcopy`, and `UIO_NOCOPY` by only advancing state.

## UIO State Utilities
- `uioadvance()` advances a `uio` by a known offset without copying.
- `uiomove_frombuf()` validates buffer/uio offsets and copies from a bounded kernel buffer.
- `ureadc()` appends a single character to a `uio`.

## IOV/UIO Allocation
- `copyiniov()` copies user iovec array into kernel memory after max-count validation.
- `copyinuio()` allocates a `uio`, copies user iovecs, sets `UIO_USERSPACE`, computes residual, and rejects overflow above `IOSIZE_MAX`.
- `allocuio()`, `freeuio()`, and `cloneuio()` manage uio+iovec storage.

## User Mapping Helpers
- `copyout_map()` maps anonymous user memory after the process data limit area for copyout-style operations.
- `copyout_unmap()` removes that mapping.

## User Word Wrappers
- `fuword32()`, `fuword64()`, `fuword()` wrap `fueword*` APIs and return `-1` on failure.
- `casuword32()` and `casuword()` wrap userspace compare-and-swap helpers.

## Kernel Interface
- Exposes `kern.iov_max` sysctl as `UIO_MAXIOV`.

## Filesystem Relevance
This file is directly used by filesystem read/write, directory read, extended attribute, ioctl, and device I/O paths. It defines the canonical semantics for advancing `uio_resid`/`uio_offset` and handling user versus kernel buffers.
