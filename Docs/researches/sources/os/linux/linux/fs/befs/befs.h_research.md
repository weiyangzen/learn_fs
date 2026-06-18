# File Research: sources/os/linux/linux/fs/befs/befs.h

## Purpose
Core private BeFS header for the Linux kernel driver. It defines in-memory BeFS superblock and inode state, shared error codes, debug function prototypes, and helper conversions between BeFS inode addresses and logical block numbers.

## Main Interfaces
- `struct befs_mount_options`: parsed mount options for uid/gid override, debug flag, and I/O charset.
- `struct befs_sb_info`: in-memory superblock fields copied from disk, including block size, byte order, allocation group geometry, journal range, root/index inode addresses, mount options, and NLS table.
- `struct befs_inode_info`: BeFS-private inode payload embedded around `struct inode`; stores inode address, parent, attributes, flags/type, and either a datastream or short symlink buffer.
- `enum befs_err`: BeFS-local status codes for generic errors and B+tree traversal states.
- `BEFS_SB()` / `BEFS_I()`: private-data accessors.
- `iaddr2blockno()` / `blockno2iaddr()`: allocation-group address conversions.
- `befs_iaddrs_per_block()`: number of BeFS inode/block-run addresses per filesystem block.

## Dependencies
Includes `befs_fs_types.h` for on-disk and host structures, and includes `endian.h` at the end so conversion helpers can use the private superblock type.

## Research Notes
This header is the coupling point between the BeFS VFS layer, datastream mapper, B+tree reader, inode validation, superblock loading, and debug helpers. The driver treats BeFS as read-only at the VFS layer, so most mutable state here is mount/session metadata rather than allocation state.
