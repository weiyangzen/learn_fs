# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/move.c

## Purpose

`move.c` implements core `uio_t` data movement helpers used throughout the kernel for copying bytes between kernel buffers, user address spaces, and kernel I/O vectors. It also contains optional asynchronous copy support using the platform dcopy/I/OAT DMA framework.

Read completely: 795 lines.

## Main Responsibilities

- Moves byte ranges through `uiomove()`, updating `uio` progress.
- Prefaults user or kernel pages referenced by a `uio` without modifying it.
- Copies through `uiocopy()` without changing the source `uio`.
- Reads or writes single bytes through `ureadc()` and `uwritec()`.
- Skips data in a `uio` with `uioskip()`.
- Duplicates a `uio` and caller-supplied iovec storage with `uiodup()`.
- Supports asynchronous copy setup, submission, and cleanup with `uioainit()`, `uioamove()`, and `uioafini()`.

## Core UIO Copy Paths

`uiomove()` iterates over iovecs, skips zero-length entries, copies up to the smaller of requested bytes and current iovec length, and advances `iov_base`, `iov_len`, `uio_resid`, `uio_loffset`, and the source pointer. It chooses copy helpers by segment flag:

- `UIO_USERSPACE` / `UIO_USERISPACE`: `xcopyout_nta()` for reads and `xcopyin_nta()` for writes.
- `UIO_SYSSPACE`: `kcopy_nta()` in the appropriate direction.

`uiocopy()` mirrors the same copy rules but leaves the original `uio` untouched and reports copied bytes through `cbytes`.

`uio_prefaultpages()` touches one byte per page and the final byte in each segment with `fuword8()` or `kcopy()` to encourage page residency before later I/O.

## Character And Cursor Helpers

`ureadc()` writes one byte into the address space represented by a `uio`, skipping empty iovecs and advancing all relevant fields. `uwritec()` reads one byte from a `uio` and returns `-1` on failure. Both reject invalid or exhausted `uio` structures.

`uioskip()` advances over `n` bytes without copying, updating the iovec cursor and offset. It refuses to skip past `uio_resid`. `uiodup()` shallow-copies the `uio` and duplicates each iovec into caller-supplied storage, failing if the destination iovec array is too small.

## Async Copy Support

The async path is built around `uioa_t` and dcopy handles:

- `uioa_dcopy_enable()` / `uioa_dcopy_disable()` toggle global async availability.
- `uioainit()` allocates a dcopy channel, copies the `uio`, validates iovec count, marks async state, locks user pages with `as_pagelock()`, and stores either page lists or synthesized PFN arrays.
- `uioamove()` supports only kernel-to-user `UIO_READ` into `UIO_USERSPACE`. It splits DMA commands on source and destination page boundaries, allocates linked dcopy commands, fills source/destination physical addresses, posts copy commands, and advances the `uioa` cursor.
- `uioafini()` optionally polls or blocks for the last dcopy command, frees commands and channel state, unlocks all locked pages, copies final `uioa` progress back into the caller's `uio`, and resets the async state.

## Dependencies

The file depends on copy primitives, `uio_t`/`iovec_t`, VM address spaces, page locking, HAT PFN translation, segkpm-style page state, dcopy channel/command APIs, and current process address-space state.

## Notable Edge Cases

- `uiomove()` and `uiocopy()` return immediately on the first copy fault, leaving progress already applied for prior iovecs.
- `uio_prefaultpages()` is best effort and silently stops on fault.
- `uioainit()` disables async copy globally if dcopy resources disappear.
- Async copy has comments noting Intel I/OAT-specific implementation assumptions.
- `uioafini()` contains an explicit comment questioning why `cmd == NULL` can occur.
- PFN-array cleanup uses the stored `uioa_pfncnt` path when `as_pagelock()` did not return page pointers.

## Research Relevance

This is a core data-transfer file for filesystem and device I/O paths. Read/write implementations commonly rely on `uiomove()` semantics for residual counts, offsets, fault handling, and kernel/user memory separation; async copy support affects high-throughput copyout behavior.
