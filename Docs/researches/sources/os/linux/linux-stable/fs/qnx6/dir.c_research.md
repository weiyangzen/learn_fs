# File Research: sources/os/linux/linux-stable/fs/qnx6/dir.c

## Summary
Implements QNX6 directory iteration and name lookup helpers, including support for long filenames stored in the filesystem's longfile metadata file.

## Main Responsibilities
- Iterate directory pages and emit short or long filenames.
- Resolve long filename records through the mounted longfile inode.
- Validate long filename size and checksum where applicable.
- Search directories for matching short or long names.
- Cache the last successful lookup page in `i_dir_start_lookup`.

## Key Interfaces
- `qnx6_readdir()` is the directory `iterate_shared` operation.
- `qnx6_find_ino()` searches a directory and returns a matching inode number.
- `qnx6_dir_operations` and `qnx6_dir_inode_operations` provide VFS operations.

## Important Behavior
Short names are stored directly in directory entries. Long names use entries with `de_size == 0xff`; the entry points to a long filename record by block number. Non-MMI filesystems verify the long-name checksum using `qnx6_lfile_checksum()`.

Lookup starts at the cached page from the previous hit and wraps around, improving repeated lookup locality in large directories.

## Cross-File Interactions
`namei.c` calls `qnx6_find_ino()`. Long-name reads use `sbi->longfile`, created in `inode.c` from the superblock's Longfile root node.

## Risks
Long filename integrity is mostly best-effort: checksum mismatches are logged but do not prevent emitting the name. Directory reads depend on the page-cache/block-map path working for both directories and the longfile inode.
