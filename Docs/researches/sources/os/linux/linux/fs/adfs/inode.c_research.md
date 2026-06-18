# File Research: sources/os/linux/linux/fs/adfs/inode.c

Implements ADFS inode creation, block mapping, address-space operations, permission/time conversion, setattr, and inode writeback.

Key behavior:
- `adfs_get_block()` maps file logical blocks through `__adfs_block_map()` for reads, but returns `-EIO` for block creation because allocation is not implemented.
- Address-space operations use buffer-head/mpage helpers for folio read, writepages, write_begin/write_end, invalidation, migration, and bmap.
- Converts ADFS/RISC OS attributes to Linux modes:
  - Directory attributes become executable directories with owner-mask read bits.
  - Filetype `0xfc0` becomes symlink.
  - Filetype `0xfe6` gets executable read masks.
  - Owner/public read/write attributes map through mount masks.
- Converts Linux mode changes back to ADFS attributes for writable metadata updates.
- Converts 40-bit RISC OS centisecond timestamps from the 1900 epoch to Unix `timespec64`.
- Converts Unix mtime back to stamped ADFS timestamp when possible.
- `adfs_iget()` creates a new inode from `object_info`, storing parent id, object id, load/exec addresses, attributes, size, uid/gid, timestamps, and operation tables.
- Uses the object indirect disk address as the inode number.
- `adfs_setattr()`:
  - Rejects uid/gid changes that differ from global mount uid/gid.
  - Handles size changes only at page-cache/inode-size level; comments note missing on-disk truncation.
  - Converts mtime and mode into ADFS metadata.
  - Marks inode dirty for size/mtime/mode changes.
- `adfs_write_inode()` reconstructs `object_info` and calls `adfs_dir_update()` to write metadata back to the parent directory entry.

Important interactions:
- Relies on immutable parent-id assumptions: metadata writeback needs the parent directory id, so cross-directory rename is not supported by this design.
- Block allocation is absent despite generic write paths being wired.
