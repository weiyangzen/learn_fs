# File Research: sources/os/linux/linux/fs/hpfs/ea.c

Purpose: Handles HPFS extended attributes stored inline in fnodes, externally in sector runs, or indirectly through anode-backed storage.

Key functions:
- `hpfs_ea_ext_remove()` walks and removes external EA lists, including indirect EA values, then frees direct sectors or anode trees.
- `get_indirect_ea()` and `set_indirect_ea()` read/write indirect EA payloads.
- `hpfs_read_ea()` copies a named EA into a caller buffer from inline, external, or indirect storage.
- `hpfs_get_ea()` allocates and returns a named EA value.
- `hpfs_set_ea()` updates an existing fixed-size EA or creates a new EA, preferring fnode-resident storage, then external sectors; it can relocate external EA runs when contiguous growth fails.

Dependencies and integration:
- Used by inode read/write paths for UID, GID, MODE, DEV, and SYMLINK EAs.
- Relies on anode EA read/write/remove helpers and sector allocation.

Risk notes:
- EA resizing is limited: existing EAs are updated only when the size matches.
- Some anode creation for EA list growth is commented out; relocation to a new contiguous run is used instead.
- EA corruption checks focus on list bounds and indirect-value metadata.
