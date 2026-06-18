# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gmisc.c

Purpose: Provides bit-level `Bigint` helpers used by generalized conversion paths.

Core behavior:
- `rshift()` shifts a `Bigint` right in-place and compacts its word count.
- `trailz()` counts trailing zero bits in a `Bigint`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `lo0bits`, `ULbits`, `kshift`, `kmask`, and NetBSD `_DIAGASSERT`.
