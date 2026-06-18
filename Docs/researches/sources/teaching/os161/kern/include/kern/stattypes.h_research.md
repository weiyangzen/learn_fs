# File Research: sources/teaching/os161/kern/include/kern/stattypes.h

Defines file type bits for `st_mode`.

Constants:
- `_S_IFMT`, `_S_IFREG`, `_S_IFDIR`, `_S_IFLNK`, `_S_IFIFO`, `_S_IFSOCK`, `_S_IFCHR`, `_S_IFBLK`.

Relevance:
- SFS and semfs map inode/object type to regular-file or directory mode bits.
- Public kernel/user stat headers expose non-underscore aliases.
