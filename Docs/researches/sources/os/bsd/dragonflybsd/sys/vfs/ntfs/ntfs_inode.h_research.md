# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_inode.h

This header defines NTFS in-memory inode and file-stream state. `struct ntnode` represents an NTFS MFT record and tracks device identity, mount, inode number, flags, locks, use count, attached fnodes, loaded attribute list, link count, main record, and file-record flags.

`struct fnode` represents a vnode-exposed NTFS attribute stream for an `ntnode`; it stores the vnode pointer, stream type/name, file times, parent inode number, NTFS file flags, size/allocation, directory read cache cursor, and directory block buffer.

It also defines inode flags such as `IN_HASHED`, `IN_LOADED`, and `IN_PRELOADED`, fnode flags such as `FN_PRELOADED`, `FN_VALID`, and `FN_AATTRNAME`, and `struct ntfid` for NFS file handles.

Research notes: NTFS separates MFT-record identity (`ntnode`) from named attribute-stream vnode identity (`fnode`), which is important for alternate data stream handling.
