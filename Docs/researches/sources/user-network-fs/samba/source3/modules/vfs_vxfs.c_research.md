# sources/user-network-fs/samba/source3/modules/vfs_vxfs.c

## Purpose
`vfs_vxfs.c` adapts Samba VFS xattr, DOS attribute, and optional POSIX ACL behavior for Veritas VxFS. It prefers VxFS-specific xattr APIs and falls back to the next VFS module when unsupported, while protecting Samba NT ACL storage.

## Important APIs, Types, and Functions
ACL helpers sort, compact, and compare ACL entries: `vxfs_sort_acl()`, `vxfs_compact_buf()`, `vxfs_compare_acls()`, and `vxfs_compare()`. With `VXFS_ACL_SHARE`, `vxfs_sys_acl_set_fd()` avoids setting identical ACLs to preserve inherited VxFS ACL inode sharing. Xattr handlers `vxfs_fset_xattr()`, `vxfs_fget_xattr()`, `vxfs_fremove_xattr()`, and `vxfs_flistxattr()` route through fd, `/proc/fd` path, or filename VxFS APIs, then fall back. `vxfs_fset_ea_dos_attributes()` maps Samba readonly DOS attributes into VxFS write-protection xattrs. `vfs_vxfs_connect()` initializes VxFS support.

## Control Flow
On connect the module calls the next VFS connect and `vxfs_init()`. For xattrs, it tries fd-based VxFS calls when possible, path-based calls for pathref/proc-fd cases, then next-module xattr calls if VxFS reports unsupported. Samba's generic `XATTR_NTACL_NAME` is mapped to restricted `system.NTACL` storage on fallback. Clients are denied direct access to the protected NTACL xattr. DOS readonly setting first updates normal Samba DOS attributes, then applies or checks VxFS write xattrs.

## State and Persistence
Persistence is on the VxFS filesystem via xattrs and ACLs. The module itself keeps no per-handle private state. It can remove old-style `user.NTACL` entries after successfully setting the current NTACL.

## Dependencies and Integration Points
It depends on VxFS wrapper functions declared in `vfs_vxfs.h` and implemented elsewhere, Samba ACL/xattr VFS operations, pathref fd helpers, and `system.NTACL` security assumptions. It registers as module `vxfs`.

## Risks
The security warning around `XATTR_USER_NTACL` is central: moving NT ACL storage to `user.*` can let local users modify Samba ACLs. Several code paths preserve and restore errno manually and mix old/new removal behavior, which can mask partial failures. Path-based fallbacks for pathref files depend on proc-fd support and race-resistant VFS semantics. ACL comparison compacts entries and ignores some mask differences by design, so tests must prove it does not skip required ACL updates.

## Test Signals
Tests should cover fd, pathref/proc-fd, and path-only xattr operations; unsupported fallback; denial of direct protected NTACL get/set/list/remove; old `user.NTACL` cleanup; readonly DOS attribute mapping; and ACL-share compare/no-op behavior under `VXFS_ACL_SHARE`.
