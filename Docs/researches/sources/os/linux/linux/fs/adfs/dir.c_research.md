# File Research: sources/os/linux/linux/fs/adfs/dir.c

Implements common ADFS directory loading, iteration, lookup, dentry comparison, and metadata update support.

Key behavior:
- Uses a global `adfs_dir_rwsem` to serialize directory reads and updates.
- Provides buffer-spanning copy helpers `adfs_dir_copyfrom()` and `adfs_dir_copyto()`.
- Reads directory buffer heads through `adfs_dir_read_buffers()`, using `__adfs_block_map()` for logical-to-physical mapping.
- Releases or forgets loaded directory buffers depending on whether dirty state should be preserved.
- `adfs_dir_read_inode()` validates that the loaded directory parent id matches the inode’s stored parent id.
- `adfs_object_fixup()`:
  - Converts RISC OS `/` characters in names to Linux `.`.
  - Avoids generated `.` and `..` names by changing the first character to `^`.
  - Optionally appends `,xyz` filetype suffixes.
- `adfs_iterate()` emits `.` and `..`, then delegates entry iteration to the selected directory format ops.
- `adfs_dir_update()` updates an object’s on-disk directory entry when write support is enabled, commits directory checksums/sequence fields, marks buffers dirty, and optionally syncs.
- Lookup is case-insensitive using an ASCII-only lowercase helper.
- Dentry operations provide case-insensitive hash/compare and enforce maximum name length.
- `adfs_lookup()` reads object info by name and instantiates an inode with `adfs_iget()`.

Important interactions:
- Format-specific callbacks come from `dir_f.c` or `dir_fplus.c`.
- Writeback from `inode.c` uses `adfs_dir_update()` to persist changed metadata.
