# File Research: sources/os/linux/linux-stable/fs/ocfs2/namei.h

Purpose: declares OCFS2 namespace/orphan entry points exported from `namei.c` to other OCFS2 modules.

Read coverage: complete file read, 38 lines.

Key contents:
- Defines DIO orphan entry naming constants: `OCFS2_DIO_ORPHAN_PREFIX` as `"dio-"` and `OCFS2_DIO_ORPHAN_PREFIX_LEN` as 4.
- Exposes `ocfs2_dir_iops`, the directory inode operation table implemented in `namei.c`.
- Declares `ocfs2_get_parent()` for export/NFS parent lookup integration.
- Declares normal and DIO orphan manipulation helpers: `ocfs2_orphan_del()`, `ocfs2_create_inode_in_orphan()`, `ocfs2_add_inode_to_orphan()`, `ocfs2_del_inode_from_orphan()`, and `ocfs2_mv_orphaned_inode_to_new()`.

Dependencies:
- Uses OCFS2 superblock, inode, dentry, buffer-head, JBD2 handle, and directory-orphan semantics defined in surrounding OCFS2 headers.

Risk and edge cases:
- Callers must respect lock ownership implied by the prototypes: several orphan helpers expect already locked inode/dinode buffers or return locked orphan directories through the implementation contract.
- The `dio-` prefix is part of on-disk orphan directory naming; changing it would break recovery of existing DIO orphan entries.
