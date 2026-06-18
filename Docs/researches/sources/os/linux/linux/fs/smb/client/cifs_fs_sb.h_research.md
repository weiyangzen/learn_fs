# File Research: sources/os/linux/linux/fs/smb/client/cifs_fs_sb.h

CIFS superblock-private state and mount-flag definitions.

The `CIFS_MOUNT_*` bitmask covers permission checking, UID/GID overrides, server inode numbers, direct I/O, xattrs, special-character remapping, POSIX paths/ACLs, Unix emulation, byte-range locking behavior, fscache, symlink mode, multiuser, strict I/O, backup intent, DFS disablement, SID-derived UID/mode, handle-cache disablement, read/write cache assumptions, and shutdown.

`struct cifs_sb_info` stores tcon links in an rbtree, list linkage, locks, master tlink, NLS table, parsed mount context, active count, atomic mount flags, prune work, RCU head, optional prefix path, serverino autodisable state, and root dentry.
