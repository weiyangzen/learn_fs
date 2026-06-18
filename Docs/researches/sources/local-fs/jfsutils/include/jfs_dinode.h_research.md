# File Research: sources/local-fs/jfsutils/include/jfs_dinode.h

Defines the 512-byte JFS on-disk inode format.

Key contents:
- Includes type, directory-tree, and extent-tree headers.
- Defines inode slot/size constants.
- `struct dinode` base area includes inode stamp, fileset, number, generation, inode extent descriptor, size, block count, links, uid/gid, mode, timestamps, ACL/EA descriptors, directory index counter, and ACL type.
- The trailing 384 bytes are a union:
  - Directory form: inline directory table plus `dtroot_t`.
  - File/special form: imap generator, xtree root bytes, device descriptor, rdev/fast symlink, and inline EA.
- Defines macros aliasing union fields such as `di_dtroot`, `di_parent`, `di_xtroot`, `di_fastsymlink`, and `di_inlineea`.
- Defines on-disk mode bits for file types, permissions, and JFS extended mode bits.

Interactions:
- Used by fsck, mkfs, debug, and inode processing modules to interpret disk inodes.
- Depends on `jfs_dtree.h` and `jfs_xtree.h` for embedded root layouts.

Research notes:
- Comments document historical OS/2 compatibility constraints that shaped the union layout.
