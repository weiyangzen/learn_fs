# File Research: sources/os/linux/linux-stable/fs/isofs/dir.c

Implements ISOFS directory iteration and filename translation.

Key paths:
- `isofs_name_translate()` lowercases ISO names, strips trailing `.;1` or `;1`, and converts remaining `;` and `/` to `.`.
- `get_acorn_filename()` applies Acorn-specific filename decoration and filetype suffix handling.
- `do_isofs_readdir()` scans directory records, handles zero-length sector padding, copies entries spanning buffer boundaries, validates record/name lengths, skips multi-extent continuation records, emits `.` and `..`, filters hidden/associated files, and chooses Rock Ridge, Joliet, Acorn, normal, or raw names.
- `isofs_readdir()` allocates a temporary page for translated names and split directory entries.
- Exports `isofs_dir_operations` and `isofs_dir_inode_operations`.

Important details:
- Inode numbers are derived from normalized block/offset for the first entry of a multi-extent sequence.
- Rock Ridge `RE` entries can return `-1` to suppress relocated directory placeholders.
- Directory records that span block buffers are assembled into temporary storage before parsing.
