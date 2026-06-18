# File Research: sources/os/linux/linux/fs/isofs/namei.c

Implements ISOFS lookup.

Key functions:
- `isofs_cmp()` compares a candidate on-disk name to the dentry name, using dentry operations when casefold/Joliet comparison rules are active.
- `isofs_find_entry()` scans directory records similarly to readdir, handles zero-length sector padding, split records, record validation, Rock Ridge/Joliet/Acorn/normal name conversion, hidden/associated filtering, and returns normalized block/offset for the matching entry.
- `isofs_lookup()` allocates one temporary page, calls `isofs_find_entry()`, gets the inode with `isofs_iget()` if found, frees the page, and returns `d_splice_alias()`.

Lookup and readdir intentionally share name translation behavior so dcache identity matches visible directory entries.
