# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/extattr.h

This header defines UFS extended attribute constants, formats, and kernel state.

Key contents:
- Defines backing file magic/version and `.attribute/system` / `.attribute/user` directory names.
- Defines per-attribute file header and per-inode attribute header.
- Defines generic packed `struct extattr` and traversal/content macros.
- Defines `struct ufs_extattr_list_entry` for each enabled attribute backing file.
- Defines `struct ufs_extattr_per_mount` for per-mount state, lock, credentials, and enabled-attribute list.
- Declares extattr start/autostart/stop/control and vnode get/set/delete/list functions.

Role:
- Provides UFS1-style extended attributes by mapping attribute names to backing files rather than changing the main inode format.
