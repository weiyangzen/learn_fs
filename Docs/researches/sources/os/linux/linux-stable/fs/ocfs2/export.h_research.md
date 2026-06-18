# File Research: sources/os/linux/linux-stable/fs/ocfs2/export.h

Purpose: Declares OCFS2's exportfs operation table.

Read coverage: complete file read, 17 lines.

Key contents:
- Includes Linux exportfs declarations.
- Exposes `extern const struct export_operations ocfs2_export_ops`.

Dependencies:
- Implemented by `export.c` and consumed by superblock setup.

Risk notes:
- No internal logic; correctness depends on `export.c` keeping the exported operation table valid.
