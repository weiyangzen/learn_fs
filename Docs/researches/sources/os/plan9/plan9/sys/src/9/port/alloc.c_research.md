# File Research: sources/os/plan9/plan9/sys/src/9/port/alloc.c

This file provides the normal kernel heap allocation layer backed by `Pool`.

Key responsibilities:
- Defines `mainmem` and `imagmem` pools with xalloc/xmerge backends.
- Wraps pool locking with deferred printing because diagnostics cannot be printed while holding pool locks.
- Implements `smalloc`, `malloc`, `mallocz`, `mallocalign`, `free`, `realloc`, `msize`, and `calloc`.
- Tracks malloc and realloc caller tags using two hidden `ulong` words before returned allocations.
- Provides `mallocsummary` and `poolsummary`.

Important implementation details:
- `smalloc` sleeps and retries until memory is available.
- `malloc` and `mallocz` return `nil` on allocation failure.
- All normal allocations are rounded by the underlying pool and may be zeroed depending on API.
- Caller-visible pointers are offset from the real pool block by `Npadlong`.

Filesystem/storage relevance:
- Core allocator for VFS objects, channels, path strings, mount entries, device state, and storage driver buffers that are not allocated as `Block`s.
