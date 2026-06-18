# File Research: sources/os/linux/linux/fs/isofs/dir.c

Implements ISOFS directory iteration and base ISO name translation.

Key functions:
- `isofs_name_translate()` lowercases ISO names, drops trailing `.;1` or `;1`, and converts remaining `;` or `/` to `.`.
- `get_acorn_filename()` applies Acorn extension naming tweaks when the directory record carries a 32-byte ARCHIMEDES extension.
- `do_isofs_readdir()` walks directory records across ISOFS blocks, handles zero-length records by advancing to the next CD sector, copies split records into a temporary buffer, validates record length, emits `.` and `..`, filters hidden/associated files according to mount options, chooses Rock Ridge, Joliet, Acorn, normal mapping, or raw names, and emits entries with normalized inode numbers.
- `isofs_readdir()` allocates one page for temporary name and directory-entry buffers.
- `isofs_fileattr_get()` reports casefold/case-nonpreserving attributes based on mount/check/mapping mode.

Exports directory file and inode operations:
- `isofs_dir_operations`: llseek, read dir, shared iterate, generic lease.
- `isofs_dir_inode_operations`: lookup and fileattr_get.
