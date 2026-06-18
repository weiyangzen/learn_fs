# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_physio.c

## Purpose
Implements raw physical I/O between devices and user buffers, bypassing the buffer cache, plus the default `minphys()` transfer limiter.

## Main Responsibilities
- Validates block-aligned `uio_offset`.
- Allocates a temporary `struct buf` from `bufpool`.
- Iterates user iovecs and splits transfers according to `minphys`.
- Locks user memory for device I/O with `uvm_vslock_device()`.
- Maps user buffers for device strategy routines using direct device mapping or `vmapbuf()`.
- Calls the supplied device `strategy()` routine.
- Waits for `B_DONE`, handles `B_ERROR`, updates iovec/uio accounting, and unlocks memory.
- Frees temporary buffer state.
- Caps transfer size to `MAXPHYS` in `minphys()`.

## Key Flow
For each iovec segment, `physio()` sets `B_BUSY | B_PHYS | B_RAW | B_READ/B_WRITE`, sets `b_blkno` from `uio_offset`, limits `b_bcount`, locks/maps the user address range, invokes strategy, sleeps at `splbio()` until completion, unmaps/unlocks, computes completed bytes from `b_bcount - b_resid`, advances the uio, and exits on error or short transfer.

## Safety Checks
- Rejects non-`DEV_BSIZE`-aligned offsets.
- Avoids signed overflow by limiting `b_bcount` to `LONG_MAX` before `minphys`.
- Asserts `minphys` and strategy do not produce invalid counts.

## Dependencies
Uses buffer pool, bio priority/sleep, UVM device memory locking, vmap/vunmap buffer helpers, and device strategy callbacks.

## Research Notes
This is a classic BSD raw I/O helper. It deliberately bypasses caching and relies on caller-provided strategy/minphys routines for device-specific constraints.
