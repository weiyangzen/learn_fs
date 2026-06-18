# File Research: sources/local-fs/xfsdump/restore/win.h

## Summary
Declares the mmap window abstraction used by the node allocator.

## Main Contents
- `segix_t` segment index type.
- `win_init()` to configure windowing over a file range.
- `win_map()` and `win_unmap()` for segment mapping and pointer invalidation.
- `win_locks_off()` and `win_locks_on()` for single-threaded phases.
- `win_getnum_mmaps()` for diagnostics.

## Risks
The API returns raw pointers and requires strict map/unmap pairing.

The lock toggle is global and assumes the caller can guarantee single-threaded access while locks are disabled.
