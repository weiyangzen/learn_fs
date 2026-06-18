# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_bio.c

## Summary
Fiber backend implementation of rump block I/O.

## Key Details
- Performs reads with `pread` and writes with `pwrite` at the requested disk offset.
- Translates host `errno` through `rumpuser__errtrans`.
- For synchronous writes, uses `fsync_range(..., FDATASYNC, ...)` when available, otherwise falls back to `fsync`.
- Always invokes the supplied biodone callback with transferred byte count and translated error.

## Notes
Unlike the pthread BIO implementation, this backend runs I/O directly in the caller's cooperative fiber context.
