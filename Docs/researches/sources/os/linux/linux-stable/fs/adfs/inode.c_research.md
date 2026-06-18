# File Research: sources/os/linux/linux-stable/fs/adfs/inode.c
- Purpose: Implements ADFS inode instantiation, block mapping, address-space operations, attribute conversion, and inode writeback.
- Main functions: `adfs_get_block`, `adfs_writepages`, `adfs_read_folio`, `adfs_write_begin`, `_adfs_bmap`, `adfs_atts2mode`, `adfs_mode2atts`, time conversion helpers, `adfs_iget`, `adfs_setattr`, `adfs_write_inode`.
- Block mapping: Resolves file fragment/offset pairs through `__adfs_block_map` and `adfs_map_lookup`.
- Metadata conversion: Maps ADFS directory attributes and load/exec timestamps to Linux mode, uid/gid, size, and timestamps.
- VFS integration: Supplies buffered address-space operations and inode update/writeback hooks.
- Risks: Timestamp encoding and ADFS filetype bits share load/exec fields; writeback must update parent directory entries through `adfs_dir_update`.
