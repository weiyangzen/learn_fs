# File Research: sources/os/linux/linux-stable/fs/ocfs2/mmap.h

Purpose: declares the OCFS2 mmap preparation hook.

Read coverage: complete file read, 7 lines.

Declared APIs:
- `ocfs2_mmap_prepare(struct vm_area_desc *desc)` installs OCFS2 VM operations and performs mmap-time inode handling.

Important dependencies:
- Uses Linux `struct vm_area_desc`; implementation is in `mmap.c`.

Risk and edge cases:
- The header exposes only mmap setup; actual fault/page-mkwrite behavior is private to `mmap.c`.
