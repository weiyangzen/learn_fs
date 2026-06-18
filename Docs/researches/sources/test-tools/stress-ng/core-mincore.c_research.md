# sources/test-tools/stress-ng/core-mincore.c

## Purpose

This module ensures memory ranges are resident by touching pages, preferably using `madvise(MADV_POPULATE_READ/WRITE)` or `mincore` to avoid unnecessary writes. It supports interruptible and non-interruptible page touching.

## Important APIs, Types, And Functions

Public APIs are `stress_mincore_touch_pages` and `stress_mincore_touch_pages_interruptible`. Internal helpers are `stress_mincore_touch_pages_slow` and `stress_mincore_touch_pages_generic`.

## Control Flow

Both public functions are gated by `OPT_FLAGS_MMAP_MINCORE`. The non-interruptible path first tries `MADV_POPULATE_READ` followed by `MADV_POPULATE_WRITE` where available. The generic path computes page count, allocates a residency vector, calls `shim_mincore` on a page-aligned start, and only increments/decrements pages not already resident. If `mincore` is absent or fails, it falls back to touching all pages. Interruptible variants stop loops when `stress_continue_flag()` clears.

## State And Persistence Behavior

The module has no persistent state. It temporarily modifies bytes by incrementing and then decrementing them to fault pages in, preserving original values if no concurrent modification occurs.

## Dependencies And Integration Points

It depends on page-size lookup, global mmap-mincore option flag, global continue flag, shim mincore, and optional `madvise` population constants. It is used by mmap/memory stressors that need deterministic page residency.

## Risks And Test Signals

Risks include touching read-only mappings, races with concurrent writers, `mincore` range alignment mistakes, and allocation failure for the vector. Test signals include no-op without flag, fallback when `mincore` fails, interruptible early exit, unchanged buffer contents after touch, and behavior on non-page-aligned buffers.
