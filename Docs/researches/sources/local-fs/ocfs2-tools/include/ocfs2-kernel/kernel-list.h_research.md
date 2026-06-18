# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/kernel-list.h

This header provides a small userspace copy of Linux kernel doubly linked-list primitives.

Key content:
- Defines `struct list_head`.
- Defines list initialization macros.
- Implements inline add, add-tail, delete, empty check, and splice operations.
- Provides `list_entry`, `list_for_each`, and `list_for_each_safe`.

Integration notes:
- Used by OCFS2 userspace code needing kernel-style list manipulation.
- Does not poison deleted entries, unlike some kernel debug variants.
