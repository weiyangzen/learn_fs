# File Research: sources/os/linux/linux/fs/ocfs2/namei.h

Role: Declares OCFS2 namespace/orphan interfaces shared outside `namei.c`.

Key contents:
- Defines direct-IO orphan name prefix constants: `OCFS2_DIO_ORPHAN_PREFIX` as `"dio-"` and `OCFS2_DIO_ORPHAN_PREFIX_LEN` as `4`.
- Exports `ocfs2_dir_iops`, the directory inode operations table implemented in `namei.c`.
- Declares `ocfs2_get_parent()` for NFS/export parent lookup.
- Declares generic orphan deletion with `ocfs2_orphan_del()`.
- Declares orphan-first inode creation and movement helpers:
  - `ocfs2_create_inode_in_orphan()`
  - `ocfs2_add_inode_to_orphan()`
  - `ocfs2_del_inode_from_orphan()`
  - `ocfs2_mv_orphaned_inode_to_new()`

Design notes:
- The header separates visible VFS namespace operations from cross-file orphan APIs used by file, truncate, append-DIO, and recovery paths.
- The `dio` flag in orphan helpers lets the same orphan directory mechanism distinguish normal unlink orphans from append direct-IO recovery entries.
