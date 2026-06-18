# File Research: sources/local-fs/xfsprogs/db/bmap_inflate.c

Implements expert-mode `bmapinflate`, a destructive/debug command that creates many copies of an inode’s first data fork mapping to build a very large bmbt. It requires reflink support, exactly one normal data fork mapping, and optionally estimates geometry without modification (`-e`). It supports choosing number of extents (`-n`) and limiting dirty btree load buffers (`-d`).

The implementation can populate an extent-format staged fork or bulk-load a btree-format fork. It allocates bmbt blocks, stages a fake root, fills records via libxfs btree bulk-load callbacks, commits the staged btree into the inode, updates inode block counts, enables large extent counts if needed, and marks the filesystem `NEEDSREPAIR`. Risk is explicit and intentional: successful mutation leaves the filesystem inconsistent and requiring `xfs_repair`.
