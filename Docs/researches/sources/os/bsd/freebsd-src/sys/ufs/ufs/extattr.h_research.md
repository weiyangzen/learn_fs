# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/extattr.h

## Purpose
Defines UFS extended attribute constants, file/header formats, in-memory per-mount attribute registration, and kernel entry points for extended attribute control and vnode operations.

## Key Contents
- File-format constants:
  - `UFS_EXTATTR_MAGIC`
  - `UFS_EXTATTR_VERSION`
  - `UFS_EXTATTR_MAXEXTATTRNAME`
- Autostart directory names:
  - `.attribute`
  - `system`
  - `user`
- Attribute flags and permissions:
  - `UFS_EXTATTR_ATTR_FLAG_INUSE`
  - `UFS_EXTATTR_PERM_KERNEL`, `ROOT`, `OWNER`, `ANYONE`
- Per-mount flags:
  - `UFS_EXTATTR_UEPM_INITIALIZED`
  - `UFS_EXTATTR_UEPM_STARTED`
- Control commands:
  - `UFS_EXTATTR_CMD_START`
  - `UFS_EXTATTR_CMD_STOP`
  - `UFS_EXTATTR_CMD_ENABLE`
  - `UFS_EXTATTR_CMD_DISABLE`
- Backing-file metadata:
  - `struct ufs_extattr_fileheader`
  - `struct ufs_extattr_header`
- Native extended attribute record layout:
  - `struct extattr`
  - `EXTATTR_NEXT`
  - `EXTATTR_CONTENT`
  - `EXTATTR_CONTENT_SIZE`
  - `EXTATTR_BASE_LENGTH`
- Registered backing attribute entry:
  - `struct ufs_extattr_list_entry`
- Per-mount extended attribute state:
  - `struct ufs_extattr_per_mount`
  - Contains `sx` lock, list of enabled attributes, credential, and flags.
- Kernel declarations:
  - `ufs_extattr_uepm_init`, `ufs_extattr_uepm_destroy`
  - `ufs_extattr_start`, `ufs_extattr_autostart`, `ufs_extattr_stop`
  - `ufs_extattrctl`
  - `ufs_getextattr`, `ufs_deleteextattr`, `ufs_setextattr`
  - `ufs_extattr_vnode_inactive`

## Interactions
- Implemented in `ufs_extattr.c`.
- ACL implementation stores POSIX.1e and NFSv4 ACLs through extended attributes.
- UFS1 uses backing files; UFS2 has native extended attribute support noted in implementation comments.
