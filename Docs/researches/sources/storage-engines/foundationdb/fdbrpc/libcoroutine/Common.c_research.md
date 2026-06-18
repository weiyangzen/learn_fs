# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.c

## Purpose

`Common.c` implements memory helper functions used by the coroutine library and optional allocation tracking when `IO_CHECK_ALLOC` is enabled. It also provides byte-order utility functions used by the old BaseKit-style support code.

## Important APIs, types, and functions

With `IO_CHECK_ALLOC`, the file defines `MemoryBlock` headers placed before each returned allocation, linked-list tracking through `baseblock()`, and wrappers `io_real_malloc()`, `io_real_calloc()`, `io_real_realloc()`, `io_free()`, `io_show_mem()`, `io_showUnfreed()`, and allocation counters. Always-built helpers are `cpalloc()`, `io_freerealloc()`, `io_isBigEndian()`, and `io_uint32InBigEndian()`.

## Control flow, state, and persistence

In tracking mode, allocations are routed through `MemoryBlock_newWithSize_file_line_()`, inserted into a global linked list, and removed on free or realloc. Counters track allocation count, realloc count, current bytes, maximum bytes, and frees. In normal builds, `Common.h` maps `io_malloc`/`io_calloc`/`io_free` directly to libc and `io_realloc` to `io_freerealloc()`, so the tracking code is compiled out. State is process-local and reset at process start; there is no persistence.

## Dependencies and integration points

`Common.h` declares these APIs and macro-selects the tracked or direct allocator path. `Coro.c` uses `io_calloc()` and `io_free()` for `Coro` objects and stacks, so out-of-memory behavior and optional leak reports flow through this file. The code depends on `stdio.h`, `string.h`, and integer typedefs from `Common.h`.

## Risks and test signals

The tracking allocator is not protected by locks, so it is unsafe if enabled for concurrent coroutine allocation. `io_real_calloc()` does not zero the user allocation, despite the `calloc` name, which would be a serious behavior mismatch if tracking mode were enabled. `io_isBigEndian()` returns the first byte of integer `1`, so its truth value is little-endian rather than big-endian; as written, `io_uint32InBigEndian()` appears inverted if it is used for host-to-big-endian conversion. Test signals include coroutine allocation/free under `COROUTINE_IMPL=libcoro`, optional `IO_CHECK_ALLOC` leak output, and endian conversion tests on little- and big-endian hosts.
