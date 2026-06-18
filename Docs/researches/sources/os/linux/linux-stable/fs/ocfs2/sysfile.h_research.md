# File Research: sources/os/linux/linux-stable/fs/ocfs2/sysfile.h

Declares the system-file inode lookup API.

Key contents:
- Declares `ocfs2_get_system_file_inode(struct ocfs2_super *osb, int type, u32 slot)`.

Integration points:
- Used by mount, allocation, quota, journal, local allocator, truncate log, recovery, and other OCFS2 internals that need typed system inodes.
- `type` selects an OCFS2 system inode kind; `slot` selects the node-local instance for local system files.

Risk areas:
- Callers must release the returned inode reference with `iput()`.
- Slot must be meaningful for local system inode types and `OCFS2_INVALID_SLOT` for global ones where appropriate.
