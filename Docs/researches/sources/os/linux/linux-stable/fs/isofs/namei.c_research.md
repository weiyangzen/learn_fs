# File Research: sources/os/linux/linux-stable/fs/isofs/namei.c

Implements ISOFS lookup.

Key paths:
- `isofs_cmp()` compares a candidate name against the dentry, using dentry-specific compare ops when present.
- `isofs_find_entry()` scans a directory for the requested name, handling sector padding, split directory records, name translation through Rock Ridge/Joliet/Acorn/normal mappings, hidden and associated-file filtering, and directory block/offset normalization.
- `isofs_lookup()` allocates one page for translated names and split records, calls `isofs_find_entry()`, loads the inode with `isofs_iget()` if found, and returns `d_splice_alias()`.

Important details:
- Lookup returns no match for special one-byte ISO `.`/`..` names via `dlen > 1 || dpnt[0] > 1`.
- Corrupt directory records with name lengths beyond the record length are rejected.
