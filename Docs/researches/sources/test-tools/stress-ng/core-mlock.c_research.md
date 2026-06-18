# sources/test-tools/stress-ng/core-mlock.c

## Purpose

This file provides a helper to `mlock` an address range after expanding it to page boundaries. It is intended for locking sensitive or latency-critical regions such as signal-handler code/data into RAM.

## Important APIs, Types, And Functions

The single public function is `stress_mlock_region`. It computes page-aligned start and end using `stress_memory_page_size_get`, calculates length, and calls `shim_mlock` when `HAVE_MLOCK` is available.

## Control Flow

If the aligned end is not after the aligned start, the function returns success without calling `mlock`. Unsupported builds return success after marking the path unexpected.

## State And Persistence Behavior

The module owns no state. Successful `mlock` changes process memory locking state until unlock or process exit and is constrained by `RLIMIT_MEMLOCK` and privileges.

## Dependencies And Integration Points

It depends on page-size lookup and shim `mlock`. It integrates with code paths that want reduced paging latency.

## Risks And Test Signals

Risks include permission or limit failures, incorrect alignment, and assuming unsupported platforms actually lock memory. Test signals include aligned ranges, zero-length ranges, failure under low `RLIMIT_MEMLOCK`, and no-op compile behavior without `mlock`.
