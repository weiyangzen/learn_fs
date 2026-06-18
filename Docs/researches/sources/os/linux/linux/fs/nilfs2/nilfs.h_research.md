# File Research: sources/os/linux/linux/fs/nilfs2/nilfs.h

`nilfs.h` is the main private header for NILFS. It defines `struct nilfs_inode_info`, the filesystem-specific inode wrapper containing inode flags, dynamic NILFS inode state, bmap storage, xattr state, dirty-list linkage, on-disk inode buffer pointer, root pointer, and embedded VFS inode.

It defines dynamic inode state bits such as `NILFS_I_DIRTY`, `NILFS_I_QUEUED`, `NILFS_I_BUSY`, `NILFS_I_COLLECTED`, `NILFS_I_UPDATED`, `NILFS_I_INODE_SYNC`, and `NILFS_I_BMAP`. These are heavily used by `segment.c` to move inodes through dirty collection, writeback, and cleanup. It also defines inode type flags for normal, GC, btree-node-cache, and shadow-cache inodes.

The header contains inode-number classification macros for metadata/system/private inodes, including DAT, cpfile, sufile, ifile, root, atime, and sketch inode ranges. These macros gate validity checks, mount behavior, and export handling.

`struct nilfs_transaction_info` and transaction flag definitions support the log-construction transaction model. Helpers inspect current task `journal_info` to detect GC or writer context.

The file declares cross-subsystem APIs for directory operations, file sync, ioctl, inode read/write/dirty/truncate/fiemap, superblock operations, GC inode access, sysfs groups, and VFS operation tables. POSIX ACL support is explicitly disabled with a compile-time error if configured, while the fallback `nilfs_init_acl()` applies umask for non-symlink inodes.
