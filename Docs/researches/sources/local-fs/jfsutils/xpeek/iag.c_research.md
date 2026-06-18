# File Research: sources/local-fs/jfsutils/xpeek/iag.c

Implements display/modification of JFS inode allocation groups (IAGs), shared bitmap display helpers, inode extent display helpers, and the `find_iag` resolver used by inode lookup.

Main command:
- `iag(void)`: parses IAG number and optional table selector:
  - default filesystem inode table,
  - `a` for primary aggregate inode table,
  - `s` for secondary aggregate inode table.
- Resolves the IAG address with `find_iag`.
- Reads the IAG with `xRead`, endian-swaps with `ujfs_swap_iag`, displays it, and writes back if changed.

Display/edit helpers:
- `display_iag(struct iag *)`: prints AG start, IAG number, free-list links, inode/extents maps, free inode/extent counts, and menu labels for working map, persistent map, and inode extents.
- `change_iag(struct iag *)`: handles modification of scalar fields, or delegates to:
  - `display_map(iag->wmap, EXTSPERIAG)`,
  - `display_map(iag->pmap, EXTSPERIAG)`,
  - `display_ext(iag->inoext, cmdline)`.
- `display_map(unsigned *map, int size)`: paginates and edits arrays of 32-bit map words; also used by `dmap.c`.
- `display_ext(pxd_t *ext, char *cmdline)`: displays/modifies one inode extent PXD by index.

Lookup:
- `find_iag(unsigned iagnum, unsigned which_table, int64_t *address)`:
  - Converts IAG number to logical block with `IAGTOLBLK`.
  - Selects the fileset inode address from primary aggregate, secondary aggregate, or filesystem table.
  - Reads the fileset inode.
  - Walks its xtree using binary search over XADs.
  - Descends internal pages until it finds a leaf covering the target logical block.
  - Returns the physical byte address of the IAG.

Integration points:
- Used by `inode.c` for `find_inode`.
- Uses `AIT_2nd_offset` initialized in `xpeek.c`.
- Uses `xRead`, `xWrite`, endian helpers, and JFS xtree/filsys macros.

Notable behavior and risks:
- `find_iag` reads the fileset inode but does not explicitly endian-swap the inode/xtree root before using `__le16_to_cpu` on `nextindex`; XAD accessor macros may handle endian details, but this is a sensitive portability area.
- `display_map` calls `m_parse(cmdline, size - 1, ...)`, while `m_parse` accepts fields starting at 1, making index 0 not directly modifiable through that path.
- Editing IAG maps/extents can easily desynchronize inode allocation metadata.
