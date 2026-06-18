# File Research: sources/local-fs/xfsprogs/db/faddr.c

Purpose: implements field-address navigation callbacks used by printable field definitions to jump from a field value to another filesystem object.

Key behavior:
- `fa_agblock` navigates from an AG-relative block field using `cur_agno`.
- `fa_agino` navigates from an AG inode number to a filesystem inode.
- `fa_attrblock`, `fa_cfileoffa`, and `fa_dfiloffa` map attribute fork logical offsets through `bmap`.
- `fa_cfileoffd` and `fa_dfiloffd` map data fork logical offsets through `bmap`, using directory geometry and `bbmap` when the target type is a directory block.
- `fa_cfsblock` and `fa_dfsbno` navigate directly from encoded filesystem block numbers.
- `fa_dirblock` maps directory logical block numbers to physical blocks, building a multi-extent buffer map when needed.
- `fa_drfsbno` navigates realtime filesystem block numbers on the realtime device.
- `fa_drtbno` navigates realtime block numbers using `set_rt_cur`.
- `fa_ino`, `fa_ino4`, and `fa_ino8` navigate from inode fields to inode buffers.
- All callbacks reject null sentinel values and report unmapped logical blocks.

Interactions:
- Function pointers are stored in `ftattrtab` entries in `field.c`.
- Uses current AG state, current inode bmap state, type table entries, `set_cur`, `set_rt_cur`, and `set_cur_inode`.
- Supports field-driven navigation in print/examine workflows.

Risks/notes:
- Many callbacks require valid contextual state, especially `cur_agno` or current inode bmap context.
- Mapped directory blocks can require composite buffer maps when logical directory blocks span multiple extents.
