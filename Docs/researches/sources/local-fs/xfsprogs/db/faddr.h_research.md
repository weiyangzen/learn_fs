# File Research: sources/local-fs/xfsprogs/db/faddr.h

Purpose: declares field-address navigation callback type and implementations.

Key contents:
- Defines `adfnc_t`, the callback signature for navigating from a field value to a next type.
- Declares address callbacks for AG blocks, AG inodes, attr blocks, compact and direct file offsets, fsblocks, directory blocks, realtime blocks, and inode-number variants.

Interactions:
- `field.h` embeds `adfnc_t` in `ftattr_t`.
- `field.c` assigns these callbacks to field types.

Risks/notes:
- Header only declares navigation helpers; behavior depends on current `xfs_db` cursor state.
