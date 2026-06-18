# File Research: sources/os/linux/linux-stable/fs/adfs/adfs.h
- Purpose: Central private header for the ADFS filesystem.
- Main types: `adfs_inode_info`, `adfs_sb_info`, `adfs_dir`, `object_info`, `adfs_dir_ops`, and `adfs_discmap`.
- Constants: Defines special fragment IDs, ADFS filetype handling, directory attribute bits, maximum exported name length, and mount-derived masks.
- Inline helpers: Provide inode/superblock container access, filetype extraction, signed shifts, block mapping via `adfs_map_lookup`, disc record mapping, and disc size calculation.
- Integration: Declares cross-file functions for inode lookup/setattr/writeback, directory operations, map reading/freeing, statfs, and error reporting.
- Risks: Many values are stored in compact historical on-disk formats; helpers centralize endian, bit-shift, and address conversion assumptions.
