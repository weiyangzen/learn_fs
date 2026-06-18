# File Research: sources/local-fs/jfsutils/libfs/diskmap.c

Implements block allocation map helper routines for buddy summaries and dmap initialization.

Key contents:
- Static `budtab[256]` maps byte bit patterns to maximum free-string values for buddy allocation summaries.
- `ujfs_maxbuddy()` computes maximum free string in a 32-bit map word, fast-pathing all-free and half-free cases before table lookup.
- `ujfs_adjtree()` computes a dmap/dmapctl summary tree by combining leaf buddy values and bubbling maxima up through parent levels.
- `ujfs_complete_dmap()` fills dmap page metadata and summary tree from initialized working/persistent maps, returning top tree max.
- `ujfs_idmap_page()` initializes a dmap page as free for existing blocks and allocated for non-existent blocks in a partial final page.
- `ujfs_getagl2size()` computes log2 allocation group size from aggregate size and maximum AG count.

Interactions:
- Uses constants and structs from `jfs_dmap.h`.
- Used by mkfs/fsck map initialization and validation flows.

Research notes:
- Core allocator geometry helper code; no disk I/O here.
- Uses unaligned casts to `uint32_t *`/`uint16_t *` in `ujfs_maxbuddy()`, which may matter on strict-alignment architectures.
