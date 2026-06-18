# sources/user-network-fs/samba/source3/modules/vfs_vxfs.h

## Purpose
This header declares the VxFS-specific wrapper functions consumed by `vfs_vxfs.c`. It abstracts platform or library calls for VxFS xattr and write-attribute support.

## Important APIs, Types, and Functions
The declarations include fd and path variants for setting, getting, removing, and listing xattrs: `vxfs_setxattr_fd`, `vxfs_getxattr_path`, `vxfs_getxattr_fd`, `vxfs_removexattr_fd`, and `vxfs_listxattr_fd`. It also declares write-attribute controls `vxfs_setwxattr_path`, `vxfs_setwxattr_fd`, `vxfs_checkwxattr_path`, `vxfs_checkwxattr_fd`, and global initialization `vxfs_init()`.

## Control Flow
`vfs_vxfs.c` calls `vxfs_init()` during VFS connect, then chooses fd/path helper calls based on Samba `files_struct` capabilities. The helpers report unsupported operations through errno values, allowing fallback to generic VFS xattr behavior.

## State and Persistence
The header has no state. Its functions act on persistent filesystem metadata managed by VxFS.

## Dependencies and Integration Points
It is tightly coupled to the VxFS wrapper implementation, likely `lib_vxfs.c`, and to Samba's VFS xattr module. The path functions must honor directory versus file behavior where the C module passes an `is_dir` flag to definitions not shown in this header, so implementation prototypes must remain consistent with compilation context.

## Risks
Prototype drift between this header and wrapper implementation would be a hard compile or ABI risk. Because callers rely on errno categories such as `ENOTSUP`, `ENOSYS`, `ENODATA`, `EOPNOTSUPP`, and `ENOENT`, wrapper implementations must preserve errno precisely.

## Test Signals
Build tests with VxFS support enabled are mandatory. Runtime tests should inject wrapper return codes and errno values to verify fallback and error mapping in `vfs_vxfs.c`.
