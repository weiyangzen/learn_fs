# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir_idx.h

Indexed-directory htree API header.

Key behavior:
- Defines `ext4_dir_idx_block`, which combines a loaded block with entry-base and current-position pointers.
- Defines `EXT4_DIR_DX_INIT_BCNT` for initial indexed directory block count.
- Declares indexed directory initialization, htree lookup, htree insertion, and parent inode reset for `..`.

Notable dependencies:
- Includes `ext4_types.h`, `ext4_fs.h`, and `ext4_dir.h`.
- Implemented by `ext4_dir_idx.c`; hash computation comes from `ext4_hash.c`.

Research notes:
- The reset-parent API is needed by directory rename/move paths for indexed directories.
