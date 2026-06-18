# File Research: sources/os/linux/linux-stable/fs/ocfs2/filecheck.h

Purpose: Defines OCFS2 online file-check status codes, queue structures, operation types, limits, and sysfs lifecycle prototypes.

Read coverage: complete file read, 64 lines.

Key contents:
- Filecheck error codes for success, generic failure, in-progress, readonly, JBD involvement, invalid inode, ECC, block number, valid-flag, generation, and unsupported cases.
- Error range macros used by status mapping.
- `struct ocfs2_filecheck` with entry list, spinlock, maximum size, current size, and completed count.
- Queue size limits: maximum 100 and minimum 10.
- Operation types for check, fix, and set-queue-size.
- `struct ocfs2_filecheck_sysfs_entry` containing kobject, unregister completion, and queue pointer.
- Prototypes for creating and removing sysfs state.

Dependencies:
- Requires Linux list/types and OCFS2 superblock context from users.

Risk notes:
- Error enum numeric values are part of the sysfs-visible behavior and must stay aligned with `filecheck.c` string mapping.
