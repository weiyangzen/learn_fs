# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/access.c

This file implements simple Unix-mode access checks for the ext2 driver.

Functions:
- `Ext2CheckInodeAccess(PEXT2_VCB Vcb, struct inode *in, int attempt)`: chooses UID/GID from `Vcb->uid/gid` or effective IDs when `VCB_USER_EIDS` is set, grants all access to root or owner, checks group mode bits for matching group, otherwise checks “other” mode bits. Returns whether the requested `attempt` mask is present.
- `Ext2CheckFileAccess(PEXT2_VCB Vcb, PEXT2_MCB Mcb, int attempt)`: wrapper that checks `Mcb->Inode`.

Dependencies:
- Uses mode helper macros such as `Ext2IsGroupReadOnly`, `Ext2IsGroupWritable`, `Ext2IsOtherReadOnly`, and `Ext2IsOtherWritable`.
- Uses access flags `Ext2FileCanRead`, `Ext2FileCanWrite`, and `Ext2FileCanExecute`.

Research notes:
- Owner/root are granted read, write, and execute regardless of individual mode bits.
- Group/other handling differentiates “read-only” and “writable” helper states and includes execute whenever read is granted.
