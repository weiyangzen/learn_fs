# File Research: sources/os/linux/linux/fs/erofs/namei.c

Implements EROFS name lookup using sorted directory blocks.

Key behavior:
- Defines internal qstr ranges for lookup comparisons.
- `erofs_dirnamecmp()` compares names while reusing already matched prefixes and tolerating corrupted on-disk names outside debug builds.
- `find_target_block()` binary-searches directory blocks by their first entry name, keeping the best candidate block.
- `find_target_dirent()` binary-searches within a directory block.
- `erofs_namei()` resolves a qstr to nid and file type or returns `-ENOENT`.
- `erofs_lookup()` rejects names longer than `EROFS_NAME_LEN`, calls `erofs_namei()`, loads the inode with `erofs_iget()`, and splices aliases.
- Directory inode operations provide lookup, getattr, listxattr, ACL retrieval, and fiemap.

Important interactions:
- Relies on EROFS directory entries being sorted alphabetically.
- Uses `erofs_bread()` for directory block access.
- Lookup returns raw on-disk nid, including possible metabox nid flag.
