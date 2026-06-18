# File Research: sources/local-fs/ocfs2-tools/extras/find_hardlinks.c

Read coverage: complete file read, 281 lines.

Purpose: walks system and root directory trees to find directory entries that reference the same inode more than once.

Behavior:
- Usage: `find_hardlinks <device-or-image> [-q]`.
- Opens the volume read-only.
- Builds an inode bitmap and duplicate-inode bitmap while recursively walking directories.
- Skips `.` and `..`; appends `/` to displayed directory paths.
- Seeds system directory and root directory inodes into the seen bitmap.
- If duplicates are found, performs a second walk and prints all paths whose inode is in the duplicate bitmap.

Dependencies: `ocfs2_dir_iterate()`, OCFS2 directory entry types, block bitmap APIs.

Risk notes:
- Read-only diagnostic.
- Recursion follows directory entries directly and assumes directory graph sanity; severe directory loops could cause repeated recursion.
- Path buffers are fixed at 4096 bytes; longer paths abort that directory walk.
