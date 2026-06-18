# File Research: sources/os/bsd/dragonflybsd/sys/sys/dmap.h

Virtual swap-to-physical swap disk map definitions.

Key responsibilities:
- Defines `NDMAP` as 38 swap map entries.
- Defines `struct dmap` with current process swap size, allocated physical swap amount, and first disk block for each chunk.
- Defines `struct dblock`, returned by swap mapping lookup, with base physical contiguous drum block and size.

Dependencies:
- Includes `sys/types.h` and `sys/blist.h`.

Notable risks:
- This is low-level VM/swap mapping state; `swblk_t` units must match VM and swap allocator expectations.
- Fixed `NDMAP` constrains direct map entries.
