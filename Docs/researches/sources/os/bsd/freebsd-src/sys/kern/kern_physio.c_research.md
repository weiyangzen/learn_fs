# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_physio.c

Read completely: 206 lines.

## Purpose
Implements `physio()`, the kernel helper for raw character-device I/O from a `uio`, splitting requests, pinning or mapping user pages, building BIOs, invoking the device strategy routine, and updating the caller's `uio`.

## Main Elements
- Validates the character device switch and normalizes too-small `si_iosize_max`.
- Rejects oversized or multi-vector I/O for devices marked `SI_NOSPLIT`.
- Allocates a BIO and chooses between direct kernel buffer use, pbuf-backed mapped user pages, or unmapped BIO page arrays for `SI_UNMAPPED`.
- For user I/O, `vm_fault_quick_hold_pages()` pins pages with read/write protection appropriate to I/O direction.
- Sets BIO command, offset, length, count, device pointer, data pointer or page-array fields, and `BIO_UNMAPPED` where applicable.
- Calls `d_strategy()` and waits with `biowait()`.
- Unmaps pbuf mappings, unholds pages, accounts block I/O/resource counters, advances iov base/resid/offset, and propagates BIO errors.
- Frees pbuf/page arrays and destroys the BIO on exit.

## Dependencies And Integration
Uses GEOM BIO allocation, cdev strategy methods, pbuf zone, VM page pinning, pmap quick mappings, unmapped buffer support, RACCT accounting, `maxphys`, and `uio` structures. This is a key bridge between device drivers and raw block-style user I/O.

## Risk Notes
Pinned-page lifetimes must exactly bracket device strategy completion. Zero progress without `BIO_ERROR` is treated as EOF. `SI_NOSPLIT` requests are rejected with `EFBIG` rather than partially processed. The read/write protection direction is intentionally inverted-looking because device reads write into user memory.
