# File Research: sources/os/linux/linux/fs/ocfs2/sysfile.h

## Purpose

`sysfile.h` declares the system-file inode lookup API used across OCFS2 subsystems.

## API Surface

- `ocfs2_get_system_file_inode(struct ocfs2_super *osb, int type, u32 slot)`

The function returns an inode reference for a global or slot-local system inode. Callers are responsible for dropping the returned reference.
