# File Research: sources/os/bsd/dragonflybsd/sys/sys/slaballoc.h

This kernel-structure header defines DragonFly's slab allocator zone and per-CPU metadata structures.

Key responsibilities:
- Defines slab sizing constants:
  - `ZALLOC_ZONE_LIMIT`
  - `ZALLOC_MIN_ZONE_SIZE`
  - `ZALLOC_MAX_ZONE_SIZE`
  - slab/oversize magic values
  - `ZALLOC_SLAB_SLIDE`
- Defines `NZONES` based on `ZALLOC_ZONE_LIMIT`.
- Defines `SLChunk` free-list node.
- Under `SLAB_DEBUG`, defines allocation source tracking entries.
- Defines `SLZone`, the in-band zone header:
  - magic
  - owner CPU/globaldata
  - zone list linkage
  - free counts and chunk bounds
  - chunk size, zone index, flags
  - local free chunks
  - remote free chunks
  - remote signal/count fields
  - optional debug source arrays
  - optional invariant bitmap
- Defines `SLZF_UNOTZEROD`.
- Defines `SLZoneList`.
- Defines `SLGlobalData`:
  - zone arrays by size class
  - free zone lists
  - free-zone count
  - junk index
  - meta-zone malloc stats

Important invariants:
- Allocations that are exact page-size multiples or `>= ZALLOC_ZONE_LIMIT` fall through to kmem.
- Most `SLZone` fields are CPU-local except `z_RChunks`; remote CPUs free through atomic operations and signal local CPUs as needed.
- `SLAB_DEBUG_ENTRIES` must be a power of two.
- `NZONES` is compile-time constrained to known zone limits.

Research notes:
- This header defines allocator internals and layout, not allocator public allocation functions.
