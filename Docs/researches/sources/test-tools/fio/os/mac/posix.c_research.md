# sources/test-tools/fio/os/mac/posix.c

## Purpose
`os/mac/posix.c` implements a macOS compatibility version of `posix_fadvise()` for fio. macOS lacks the POSIX API, so fio maps common advice values to `fcntl(F_RDAHEAD)` and cache invalidation using `mmap()` plus `msync(MS_INVALIDATE)`.

## Important APIs, Types, and Functions
`posix_fadvise()` is the exported function. `set_readhead()` toggles read-ahead with `F_RDAHEAD`. `discard_pages()` aligns an offset/length to page boundaries, maps file ranges in chunks up to `MMAP_CHUNK_SIZE`, invalidates cached pages with `msync()`, and unmaps them.

## Control Flow
`posix_fadvise()` switches on advice: `NORMAL` is a no-op, `RANDOM` disables read-ahead, `SEQUENTIAL` enables read-ahead, `DONTNEED` calls `discard_pages()`, and unknown advice returns `EINVAL`. `discard_pages()` loops over large ranges in bounded 16 GiB mappings, preserving and returning errno from `mmap()`, `msync()`, or `munmap()` failures.

## State and Persistence
The file does not persist fio state. It may alter kernel read-ahead behavior for an fd and invalidate page-cache residency for mapped file ranges. It logs errors through fio's logging layer.

## Dependencies and Integration Points
It depends on macOS `fcntl`, `mmap`, `msync`, `munmap`, page-size `sysconf()`, `MIN()`, and `log_err()`. `os-mac.h` includes `mac/posix.h` and defines `CONFIG_POSIX_FADVISE`, allowing common fio fadvise paths to compile on macOS.

## Risks and Edge Cases
Offset and length alignment expands the invalidation range to page boundaries. The implementation is documented as slower under Rosetta. Mapping with `PROT_NONE|MAP_SHARED` can fail for file types or ranges not mappable by macOS. Very large ranges rely on chunking to avoid oversized mappings.

## Test Signals
Tests should cover each advice value, invalid advice, unaligned ranges, ranges larger than 16 GiB, non-mappable fds, and fio workloads using `fadvise_hint=random/sequential/dontneed` on macOS.
