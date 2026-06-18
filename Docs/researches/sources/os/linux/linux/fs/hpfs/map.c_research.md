# File Research: sources/os/linux/linux/fs/hpfs/map.c

Purpose: Maps HPFS on-disk metadata structures into memory and performs optional consistency checks.

Key functions:
- `hpfs_map_dnode_bitmap()` maps the directory-band bitmap.
- `hpfs_map_bitmap()` maps a main bitmap block through the bitmap directory and prefetches the next bitmap.
- `hpfs_prefetch_bitmap()` issues bitmap readahead.
- `hpfs_load_code_page()` loads the first HPFS codepage and builds upper/lowercase tables.
- `hpfs_load_bitmap_directory()` loads the bitmap directory into memory.
- `hpfs_load_hotfix_map()` loads sector remapping pairs from the spare block hotfix map.
- `hpfs_map_fnode()` maps and validates an fnode, including magic, B+ tree counters, and EA bounds.
- `hpfs_map_anode()` maps and validates an anode.
- `hpfs_map_dnode()` maps and validates a 4-sector dnode, including magic, self pointer, dirent sizes, sentinel entry, and down pointers.
- `hpfs_fnode_dno()` returns a directory fnode’s root dnode sector.

Dependencies and integration:
- Uses buffer mapping helpers and HPFS superblock state.
- Provides validation gates for allocation, directory, inode, and file code.

Risk notes:
- Validation depth depends on mount check level.
- Dnode validation prevents malformed dirent sizes from causing infinite loops or out-of-bounds traversal.
