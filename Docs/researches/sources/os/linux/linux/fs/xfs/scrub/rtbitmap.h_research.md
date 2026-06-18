# File Research: sources/os/linux/linux/fs/xfs/scrub/rtbitmap.h

## Purpose
Defines shared state and helpers for realtime bitmap scrub and repair.

## Major Components
- `xrep_wordoff_t` and `xrep_wordcnt_t`: xfile word addressing types for staged bitmap content.
- `XREP_RTBMP_WORDMASK`: mask for rounding realtime extents to bitmap word boundaries.
- `struct xchk_rtbitmap`: per-scrub state including geometry, repair staging, expected free/used cursors, lock flags, xfile write position, and flexible word buffer.
- `xchk_rtbitmap_wordcnt`: computes repair buffer size.
- `xrep_setup_rtbitmap`: repair setup declaration or stub.

## Control Flow and Invariants
The flexible `words[]` buffer is empty for scrub-only mode and one fsblock worth of words for repair mode. Repair uses this buffer to bulk-fill staged bitmap words in an xfile.

## Dependencies and Integration
Shared by `rtbitmap.c` and `rtbitmap_repair.c`; also depends on online repair configuration for temporary exchange state.

## Risk and Edge Cases
Buffer sizing depends on whether repair can run. Callers must allocate `struct xchk_rtbitmap` with `kzalloc_flex` using `xchk_rtbitmap_wordcnt`.
