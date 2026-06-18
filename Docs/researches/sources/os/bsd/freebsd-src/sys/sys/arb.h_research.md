# File Research: sources/os/bsd/freebsd-src/sys/sys/arb.h

Array-backed red-black tree macro library.

Key elements:
- Defines array RB tree heads and entries for 8-, 16-, and 32-bit indexes.
- Maintains root, free-list, min, max, current count, and maximum count indexes.
- Provides allocation-size, initialization, node/index accessor, free-list, rotation, insert-color, remove-color, insert, remove, find, nearest-find, next/prev, min/max, reinsert, and traversal macros.
- Supports optional `ARB_AUGMENT` hooks.

Dependencies:
- Includes `sys/cdefs.h`.
- Uses integer typedefs, `intptr_t`, `uint8_t`, and `__DECONST` from context.

Research notes:
- Designed for preallocated arrays rather than pointer-allocated nodes.
- Useful when kernel structures need bounded allocation and stable compact indexes.
- The implementation caches min/max indexes and recycles removed nodes through an internal free list.
