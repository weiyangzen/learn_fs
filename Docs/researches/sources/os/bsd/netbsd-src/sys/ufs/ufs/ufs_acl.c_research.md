# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_acl.c

This file implements UFS POSIX.1e and NFSv4 ACL support on top of extended attributes and inode mode bits.

Key responsibilities:
- Synchronizes POSIX ACL entries from inode mode and inode mode from ACL entries.
- Retrieves NFSv4 ACLs from extended attributes, falling back to mode-derived trivial ACLs when absent.
- Retrieves POSIX.1e ACLs from old ACL extended attributes, synthesizing access ACLs from inode mode when absent.
- Sets NFSv4 ACLs, removing trivial ACL attributes and updating inode mode from ACL semantics.
- Sets or deletes POSIX.1e ACLs, storing old ACL format in extended attributes and updating inode mode for access ACLs.
- Validates POSIX.1e and NFSv4 ACLs for vnode operations.

Important behavior:
- Corrupt or wrong-sized ACL extended attributes are treated as protection failures and return `EPERM`.
- NFSv4 ACL set checks reserve space for chmod-driven entry splitting and canonical entries.
- POSIX.1e access ACL updates are non-atomic with respect to extended attribute and inode mode changes.
