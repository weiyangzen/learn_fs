# File Research: sources/os/linux/linux/fs/affs/affs.h

Defines AFFS internal structures, macros, mount flags, helper wrappers, and cross-file prototypes.

Key behavior:
- Provides macros for interpreting AFFS block headers/tails, root blocks, and data blocks.
- Defines cache sizing constants for linear and associative extended-block caches.
- `struct affs_inode_info` stores open count, link/ext/hash locks, metadata buffer tracking, block/ext counts, extension caches, last allocation/preallocation state, protection bits, mmu-private size, and embedded VFS inode.
- `struct affs_bm_info` records bitmap block number and free count.
- `struct affs_sb_info` stores partition geometry, data block size, root block, hash size, mount flags, uid/gid/mode overrides, root and bitmap buffers, prefix/volume symlink state, delayed superblock work, and RCU head.
- Defines mount flags for international mode, valid bitmap, immutable protection bits, quiet chmod errors, forced uid/gid/mode, MUFS, OFS, prefix allocation, verbose, and no filename truncation.
- Declares AFFS functions for hash insertion/removal, header removal, checksums, date/protection conversion, errors, names, bitmap allocation/freeing, namei operations, inode operations, file operations, directory operations, symlink operations, and export ops.
- Provides block access wrappers that validate block ranges before calling buffer-head helpers.
- Provides checksum adjustment helpers for header and bitmap blocks.
- Provides lock helpers for link, directory/hash, and extension operations.

Important interactions:
- Shared by all AFFS implementation files.
- Metadata buffer tracking is used so directory/hash changes can be marked dirty against inode metadata.
