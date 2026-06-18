# File Research: sources/os/linux/linux/fs/isofs/inode.c

Main ISO9660 filesystem implementation: superblock setup, mount option parsing, inode cache, dentry comparison, block mapping, inode reading, fs registration, and module lifecycle.

Mount/context handling:
- Defines `struct isofs_options` and fs parameter table for `norock`, `nojoliet`, `hide`, `showassoc`, `cruft`, `utf8`, `iocharset`, `map`, `session`, `sbsector`, `check`, uid/gid, mode/dmode, `overriderockperm`, block size, and `nocompress`.
- `isofs_init_fs_context()` sets defaults: normal mapping, Rock Ridge and Joliet enabled, blocksize 1024, unset modes, root uid/gid, auto check mode, no specific session/sbsector.
- `isofs_parse_param()` parses options for initial mount only.
- `isofs_reconfigure()` allows readonly reconfiguration only.
- `isofs_show_options()` reconstructs effective mount options.

Superblock setup:
- `isofs_fill_super()` validates block size, resolves multisession start, scans volume descriptors, detects ISO, High Sierra, and Joliet supplementary descriptors, enforces readonly, sets zone size and maximum file size, sets time range, possibly switches to Joliet root, loads NLS, initializes `isofs_sb_info`, reads root inode, chooses Rock Ridge over Joliet unless disabled/broken, installs dentry ops, export ops, super ops, and root dentry.
- Handles broken media cases where primary/Rock Ridge root is unusable or empty but Joliet root works.

Dentry operations:
- Case-sensitive and case-insensitive hash/compare variants exist, plus Joliet/MS variants that ignore trailing periods.
- Selected based on Joliet level and `check=relaxed`.

Block mapping and read path:
- `isofs_get_blocks()` maps logical file blocks to disk blocks, following ISO9660 Level 3 multi-extent sections through chained inodes and limiting runaway chains.
- `isofs_get_block()`, `isofs_bmap()`, `isofs_bread()`, `_isofs_bmap()`, `isofs_read_folio()`, and `isofs_readahead()` provide buffer-head/mpage read support.
- `isofs_aops` supports read_folio, readahead, and bmap.

Inode reading:
- `isofs_read_inode()` reads the directory record, handles records spanning blocks, assigns inode number from normalized block/offset, sets default file/dir modes, uid/gid, timestamps, extent, size, blocks, and multi-extent metadata.
- Applies `cruft` size truncation, rejects interleaved file data by zeroing size, invokes Rock Ridge parser for POSIX metadata/symlinks/devices/compression, then applies mount overrides for uid/gid/modes.
- Installs operations for regular files, directories, symlinks, and special files. Compressed files use `zisofs_aops`; symlinks use `isofs_symlink_aops`.

Inode identity:
- `__isofs_iget()` uses `iget5_locked()` keyed by metadata block and offset. Directory block/offset normalization makes aliases stable for lookup and NFS export.

Lifecycle:
- Creates/destroys `isofs_inode_cache`.
- Initializes optional zisofs support.
- Registers `iso9660` filesystem with `FS_REQUIRES_DEV`.
