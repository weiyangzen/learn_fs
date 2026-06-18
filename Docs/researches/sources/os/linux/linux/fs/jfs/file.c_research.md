# File Research: sources/os/linux/linux/fs/jfs/file.c

## Purpose
Defines JFS regular-file VFS operations, fsync, open/release allocation-group accounting, and setattr/truncate behavior.

## Key Functions
- `jfs_fsync()` writes the requested file range, locks the inode, flushes the journal if no relevant inode dirty state remains, otherwise commits the inode synchronously and maps commit failure to `-EIO`.
- `jfs_open()` rejects regular files with negative size, initializes quotas through `dquot_file_open()`, and for newly opened empty writable regular files marks an active allocation group to reduce append fragmentation.
- `jfs_release()` decrements the active allocation-group counter and clears `ji->active_ag`.
- `jfs_setattr()` validates attributes, initializes/transfers quotas for uid/gid changes, waits for direct I/O before size changes, truncates through `jfs_truncate()`, copies attributes, marks the inode dirty, and updates ACLs on chmod.

## Exported Operation Tables
- `jfs_file_inode_operations`: listxattr, setattr, fileattr get/set, and optional ACL get/set.
- `jfs_file_operations`: open, llseek, generic buffered read/write, mmap prepare, splice, fsync, release, ioctl, compat ioctl, and lease support.

## Dependencies
- Calls into JFS dmap active-AG state (`bmap->db_active`), transaction/journal code, quota code, xattr/ACL code, and ioctl helpers.
- `jfs_setattr()` uses `jfs_truncate()` from `inode.c`.

## Notable Behavior
- Empty writable files are associated with the AG containing their inode extent; the allocator uses `db_active` to avoid multiple actively growing files in one AG.
- The code uses `nop_mnt_idmap` for idmapped-mount interactions in current call sites.
