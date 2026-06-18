# File Research: sources/os/linux/linux-stable/fs/befs/befs.h

This is the central private BeFS header. It defines the in-memory BeFS superblock state, inode state, common error/result enum, debug API declarations, and key address conversion helpers used by the rest of `fs/befs`.

Key definitions:
- `BEFS_VERSION` identifies the driver as `0.9.3`.
- `befs_blocknr_t` is the host-side block number type.
- `struct befs_mount_options` stores mount-time UID/GID override flags, debug flag, and `iocharset`.
- `struct befs_sb_info` mirrors the BeFS superblock in host byte order and stores allocation group geometry, journal metadata, root/index inode addresses, mount options, and loaded NLS table.
- `struct befs_inode_info` embeds `struct inode` and stores BeFS-specific inode number, parent, attribute inode, flags/type, and either a datastream or short symlink body.
- `enum befs_err` is the internal status vocabulary shared by btree, datastream, inode, and mount validation code.

Important inline helpers:
- `BEFS_SB()` retrieves `super_block->s_fs_info`.
- `BEFS_I()` converts a VFS inode to `struct befs_inode_info`.
- `iaddr2blockno()` maps a BeFS allocation-group address to a linear block number.
- `blockno2iaddr()` performs the reverse mapping for one-block inode addresses.
- `befs_iaddrs_per_block()` computes how many disk inode-address records fit in one filesystem block.

Integration:
- Includes `befs_fs_types.h` for on-disk types, and includes `endian.h` at the end so endian helpers can depend on `BEFS_SB()`.
- Debug prototypes are implemented in `debug.c`.
- Address helpers are used heavily by `io.c`, `datastream.c`, `linuxvfs.c`, and inode validation.

Risk notes:
- The correctness of almost all disk addressing depends on `ag_shift` and `blocks_per_ag` having been validated by `super.c`.
- `iaddr2blockno()` assumes the allocation-group address has already been bounds-checked when needed.
