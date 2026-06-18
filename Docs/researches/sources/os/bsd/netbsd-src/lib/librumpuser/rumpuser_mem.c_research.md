# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_mem.c

## Summary
Memory allocation and mapping hypercalls for rumpuser.

## Key Details
- `rumpuser_malloc` uses `posix_memalign`, defaulting zero alignment to pointer-size alignment.
- Invalid alignment from `posix_memalign` is treated as a fatal programming error and aborts after printing a message.
- `rumpuser_free` delegates to `free`.
- `rumpuser_anonmmap` maps anonymous private memory with read/write and optional execute permissions.
- Uses `MAP_ALIGNED(alignbit)` when available; otherwise warns if explicit alignment was requested.
- `rumpuser_unmap` calls `munmap`.

## Notes
Errors are returned through `ET`, so non-NetBSD hosts translate mapping/allocation errno values to rump errno values.
