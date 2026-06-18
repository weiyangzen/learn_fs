# File Research: sources/local-fs/jfsutils/mkfs/inodemap.h

Header for inode-map initialization.

Declares:
- `init_inode_map(int, FILE *, int64_t, int, int64_t, int, unsigned short, int, unsigned)`

Includes `devices.h` for device I/O types.

Filesystem relevance: exposes inode allocation map construction to the mkfs aggregate/fileset creation flow.
