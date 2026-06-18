# File Research: sources/os/linux/linux/fs/ocfs2/export.h

Header for OCFS2 NFS export integration.

Exports:
- `extern const struct export_operations ocfs2_export_ops;`

Role:
- Lets the OCFS2 superblock setup install the export operation table implemented in `export.c`.

Dependencies:
- Includes Linux `exportfs.h` for `struct export_operations`.
