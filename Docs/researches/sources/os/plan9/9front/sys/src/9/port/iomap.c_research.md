# File Research: sources/os/plan9/9front/sys/src/9/port/iomap.c

I/O port range allocator and `/dev/arch/ioalloc` reporting support.

Key responsibilities:
- Tracks allocated and reserved I/O ranges in a sorted linked list of `IOMap` entries.
- Initializes a small static free-list of map records in `iomapinit()`.
- Reserves future allocation windows with `ioreserve()` and `ioreservewin()`.
- Allocates I/O port ranges with `ioalloc()`, including consumption of reserved ranges.
- Releases ranges with `iofree()`.
- Checks whether a range is unused except for reservations through `iounused()`.
- Exposes a text dump through the `ioalloc` arch file.

Important behavior:
- `iomap.mask` defines valid address bits and rounding/alignment for an architecture.
- `ioalloc(-1, ...)` reserves and then allocates a free range above `0x400`.
- Tags are truncated to 12 visible characters.

Notable risks:
- The range list assumes correct sorted insertion by callers walking insertion points.
- A collision prints the conflicting range and returns `-1`; it does not attempt relocation.
