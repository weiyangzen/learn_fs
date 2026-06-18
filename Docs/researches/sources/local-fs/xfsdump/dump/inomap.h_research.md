# File Research: sources/local-fs/xfsdump/dump/inomap.h

This header declares the inode map interface shared between dump content code and the inomap implementation.

Key API:
- `inomap_build`: constructs the in-memory inode map, prunes non-selected inodes/directories, and returns stream startpoints.
- `inomap_getsz`: returns serialized hunk size.
- `inomap_skip`: marks selected inodes as not dumped, used by `var_skip`.
- `inomap_writehdr`: copies inomap metadata into the content inode header.
- `inomap_dump`: writes the map to media.
- `inomap_alloc_context`, `inomap_reset_context`, `inomap_free_context`: manage iterator/search contexts.
- `inomap_get_state`, `inomap_get_gen`: query selected inode state and generation.
- `inomap_next_nondir`, `inomap_next_dir`: generator-style iteration over selected non-directories/directories.

Data format:
- Defines `MAP_*` state values.
- Defines `seg_t`, which stores a base inode and three 64-bit state bitmaps.
- Defines `hnk_t`, a fixed-size hunk of map segments plus `maxino`; `nextp` remains only for binary compatibility.

Important invariant:
- The comments describe “two bits” in one place, but the actual implementation and later comment use three bit planes for eight states.
