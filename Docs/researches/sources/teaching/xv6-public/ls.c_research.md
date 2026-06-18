# File Research: sources/teaching/xv6-public/ls.c

User-space directory listing utility.

Behavior:
- `fmtname` returns a blank-padded `DIRSIZ` display name.
- For files, prints name, type, inode number, and size.
- For directories, reads `struct dirent` records, stats each child path, and prints metadata.
- Handles path-too-long and open/stat errors.

Role:
- Exercises directory reading, stat, and path traversal semantics.
