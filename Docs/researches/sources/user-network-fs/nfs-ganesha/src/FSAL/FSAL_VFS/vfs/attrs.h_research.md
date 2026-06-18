# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.h

Purpose: this header declares VFS sub-FSAL attribute and ACL hook functions.

Important APIs: `vfs_acl_init`, `vfs_sub_getattrs`, and `vfs_sub_setattrs`. The get/set hooks accept a VFS object handle, an fd, requested attribute mask, and an attrlist.

Control flow and state: base VFS file and handle code call these hooks through `sub_ops` to extend POSIX attributes with referrals and optional ACL data. `vfs_acl_init` is meaningful in debug ACL builds.

Dependencies and integration points: includes `../vfs_methods.h` for VFS handle types and FSAL attr structures. Implemented by `vfs/attrs.c`.

Risks: declarations are unconditional while implementations vary by compile flags; callers must tolerate no-op behavior when ACL support is disabled.

Test signals: compile all ACL flag combinations and verify the same symbols are provided.
