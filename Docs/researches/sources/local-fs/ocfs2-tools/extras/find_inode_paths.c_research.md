# File Research: sources/local-fs/ocfs2-tools/extras/find_inode_paths.c

Read coverage: complete file read, 207 lines.

Purpose: finds all directory paths pointing to a requested inode block number.

Behavior:
- Usage: `find_inode_paths <device-or-image> <inode #>`.
- Opens the volume read-only.
- Recursively walks the system directory and root directory.
- Prints `[found] <inode> <path>` for every matching directory entry.
- Has trace-printing support but `quiet` is hard-coded on in `main()`.

Dependencies: `ocfs2_dir_iterate()`, OCFS2 superblock root/system directory block fields, and libocfs2 allocation helpers.

Risk notes:
- Read-only diagnostic.
- Fixed 4096-byte path buffer.
- Does not guard against cycles beyond whatever directory iterator and on-disk structure provide.
