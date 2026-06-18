# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dinode.h

Defines the 512-byte on-disk JFS inode format and persistent mode/flag bits.

Structure:
- Base inode area stores identity, extent descriptor, size/block counts, link count, uid/gid/mode, timestamps, ACL/EA descriptors, directory index state, and ACL type.
- Extension union overlays directory inline index plus dtree root, regular-file xtree root, imap generator, device descriptor, fast symlink storage, and inline EA space.
- Macros provide named access to union overlays such as `di_dtroot`, `di_xtroot`, `di_fastsymlink`, and `di_inlineea`.

Flags:
- Defines JFS extended mode bits for journaling, sparse files, inline EA availability, swapfile, OS/2 attributes, archive/name flags, and Linux-visible file flags.
- `JFS_FL_USER_VISIBLE`, `JFS_FL_USER_MODIFIABLE`, and `JFS_FL_INHERIT` are used by ioctl/fileattr logic.

Risk notes:
- Layout compatibility with OS/2 JFS is explicit; changing union layout would be on-disk format breaking.
