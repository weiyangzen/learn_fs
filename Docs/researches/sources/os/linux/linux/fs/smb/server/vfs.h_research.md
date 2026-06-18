# File Research: sources/os/linux/linux/fs/smb/server/vfs.h

Declares ksmbd VFS data structures, stream constants, create-option flags, and VFS helper APIs.

Key contents:
- Stream type enum for data streams and directory/index-allocation streams.
- Create option flags for tree connection, oplock filter reservation, readonly, and internal special handling.
- `ksmbd_dir_info`, `ksmbd_readdir_data`, and `ksmbd_kstat` structures used for directory enumeration and stat formatting.
- Prototypes for create, mkdir, read/write, fsync, remove, link, getattr, rename, truncate, copy ranges, xattrs, stream xattr names, path lookup/create/remove flows, empty directory check, fadvise, zero data, allocated ranges, unlink, stat conversion, lock wait/unblock, ACL/security descriptor xattrs, DOS attribute xattrs, and POSIX ACL init/inherit.

Role in subsystem:
- Public VFS abstraction boundary used by SMB command handlers and ACL/security code.
