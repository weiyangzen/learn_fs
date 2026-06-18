# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdbuffer.h

## Purpose

`fdbuffer.h` declares the kernel `fdbuffer` abstraction used to describe file data I/O buffers backed either by VM pages or by a kernel/user address range. It is used by UFS extended vnode operations and the common `fdbuffer.c` implementation.

## Main Types

`fdb_type_t` distinguishes page-backed buffers (`FDB_PAGEIO`) from address-backed buffers (`FDB_VADDR`).

`fdb_holes_t` is a linked list of sparse file holes, each carrying an offset and length.

`fdbuffer_t` tracks buffer type, state flags, length, completed I/O count, dispatched I/O count, error and residual status, parent `buf_t`, pages/address backing, hole list, direct-I/O shadow pages, owning process, asynchronous completion callback, callback argument, and a mutex protecting asynchronous counters and state.

## Interfaces and Flags

State flags include `FDB_READ`, `FDB_WRITE`, `FDB_DONE`, `FDB_ERROR`, `FDB_ASYNC`, `FDB_SYNC`, `FDB_ICALLBACK`, and `FDB_ZEROHOLE`.

Public kernel routines create buffers (`fdb_page_create()`, `fdb_addr_create()`), register completion callbacks (`fdb_set_iofunc()`), inspect holes/errors (`fdb_get_holes()`, `fdb_get_error()`), add holes (`fdb_add_hole()`), set up `buf_t` I/O (`fdb_iosetup()`), complete I/O (`fdb_iodone()`, `fdb_ioerrdone()`), free buffers (`fdb_free()`), and initialize the subsystem (`fdb_init()`).

## Research Notes

This header is filesystem-relevant because it represents sparse-aware file data buffers and direct/page I/O state. The comments document important semantics: asynchronous users must either cover the full range or finish with `fdb_ioerrdone()`, callbacks own freeing, and zeroing of holes is deferred to avoid zeroing pages while holding UFS locks.
