# File Research: sources/os/linux/linux/fs/omfs/inode.c

OMFS inode, superblock, mount, writeback, and module registration implementation.

Main responsibilities:
- Provide safe block reads in OMFS block/cluster numbering through `omfs_bread()`.
- Allocate and initialize new VFS inodes with OMFS operation tables.
- Serialize dirty VFS inode state back into OMFS on-disk inode blocks and mirrored copies.
- Read OMFS inode blocks into VFS inodes with mount-option ownership and masks.
- Manage inode eviction and free bitmap cleanup.
- Parse mount options and fill the superblock from disk metadata.
- Register/unregister the `omfs` filesystem type.

Inode write/read behavior:
- `omfs_new_inode()` allocates `s_mirrors` contiguous blocks for a new inode, sets mode-specific operations, initializes timestamps, hashes the inode, and marks it dirty.
- `omfs_update_checksums()` computes the body CRC-CCITT and header XOR checksum.
- `__omfs_write_inode()` writes type, body size, version, magic, size, ctime in milliseconds, checksums, and mirrored inode copies.
- `omfs_iget()` validates the on-disk self pointer, assigns configured uid/gid, reconstructs timestamps from milliseconds, installs file or directory operations, and unlocks the inode.
- `omfs_evict_inode()` truncates page cache, frees regular-file extents for unlinked files, then clears inode allocation bits.

Superblock and mount flow:
- `omfs_fill_super()` allocates `omfs_sb_info`, applies parsed options, reads the primary superblock at block 0, validates `OMFS_MAGIC`, and loads block counts, block sizes, mirror count, root block, and system block size.
- It validates maximum block count, system block size, filesystem block size, bitmap location, and cluster size.
- It switches Linux blocksize to `s_sys_blocksize` and computes `s_block_shift` for mapping OMFS cluster numbers to Linux block numbers.
- It reads the OMFS root block, checks consistency with the superblock, loads bitmap location and cluster size, initializes the in-memory bitmap, loads the root directory inode, and creates the VFS root dentry.
- `omfs_get_imap()` loads the on-disk bitmap into per-block memory chunks; if the filesystem has no bitmap inode (`~0ULL`), it returns success without allocating `s_imap`.

Mount options:
- Supports `uid`, `gid`, `umask`, `dmask`, and `fmask` through fs_context parsing.
- Remount parameter changes are ignored.
- Defaults are current uid, current gid, and current umask for both file and directory masks.
- `omfs_show_options()` prints only options differing from current defaults.

Super operations and module hooks:
- `omfs_sops`: write_inode, evict_inode, put_super, statfs, show_options.
- `omfs_fs_type`: block-device filesystem named `omfs`, with fs_context support and `FS_REQUIRES_DEV`.
- Module init/exit register and unregister the filesystem.

Important invariants and risks:
- The driver assumes system block size is a valid power-of-two divisor relationship with filesystem block size when computing `s_block_shift`.
- `omfs_put_super()` frees `s_imap` as a pointer array but does not free each bitmap chunk; error paths in `omfs_get_imap()` do free chunks.
- `omfs_evict_inode()` clears exactly two inode blocks, while allocation used `s_mirrors`; this is notable if mirror count differs from two.
