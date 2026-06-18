# File Research: sources/os/linux/linux-stable/fs/nilfs2/nilfs.h

`nilfs.h` is the local central header for NILFS. It defines `struct nilfs_inode_info`, embedding the VFS inode plus NILFS state: flags, inode type, dynamic state bits, bmap storage, xattr pointer, directory lookup hint, GC checkpoint number, associated inode for btree/shadow caches, dirty-list node, optional xattr semaphore, raw inode buffer, and current root pointer.

The dynamic inode state enum tracks lifecycle and segment-constructor coordination: new, dirty, queued, busy, collected, updated, inode-sync blocked, and bmap-attached states. In-memory inode type flags distinguish normal, GC, btree-node-cache, and shadow-cache inodes. Inode-number macros define metadata/system/private inode classification and validate user/system inode ranges.

The header defines NILFS transaction context (`struct nilfs_transaction_info`) stored in `current->journal_info`. Flags indicate dynamic allocation, sync construction request, GC context, segment-constructor writer context, and whether a commit happened. Inline helpers expose transaction flag setting/testing and convenience checks for GC/construction contexts.

It declares cross-file APIs for directory operations, file sync, ioctls, inode allocation/loading/dirtying/truncation/fiemap, superblock management, GC inode reads, sysfs, operation tables, and filesystem type registration. It also centralizes logging macros (`nilfs_msg`, `nilfs_error`, severity wrappers) and inode flag inheritance/masking rules.

Important mount/filesystem constants include `NILFS_MAX_VOLUME_NAME`, `NILFS_ATIME_DISABLE`, superblock commit flags, and inherited file flags. This header is the common dependency tying VFS, metadata files, segment writer, recovery, and mount code together.
