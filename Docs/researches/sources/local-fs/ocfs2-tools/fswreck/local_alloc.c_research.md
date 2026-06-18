# File Research: sources/local-fs/ocfs2-tools/fswreck/local_alloc.c

This file creates corruptions in slot-local allocation system inodes.

Key behavior:
- `get_local_alloc_window_bits()` returns a fixed test window of 256 bits.
- `create_local_alloc()` populates an empty local alloc inode by allocating clusters, setting `la_bm_off`, total/used bitmap counts, and clearing the bitmap.
- `damage_local_alloc()` mutates local alloc metadata:
  - invalid `la_size`
  - nonzero used count with zero total
  - nonzero bitmap offset with zero total
  - bitmap offset overrun or straddle
  - bitmap total larger than bitmap capacity
  - used count greater than total
- Public wrappers resolve the slot’s local alloc system inode and optionally create a non-empty local alloc before damaging bitmap/used cases.

Integration notes:
- Requires `OCFS2_LOCAL_ALLOC_FL` system inode.
- Some corruption types cannot run on an empty local alloc and warn/return.
