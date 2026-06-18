# File Research: sources/teaching/minix/minix/fs/ext2/glo.h

This header declares ext2 server globals, with `_TABLE` controlling definition versus `extern`.

Globals:
- `err_code`: temporary error return storage.
- `cch[NR_INODES]`: declared cache-related array, initialized in `main.c`.
- `fs_dev`: current filesystem device.
- `group_descriptors_dirty`: signals pending group descriptor writeback.
- `opt`: runtime mount/server options.
- `le_CPU`: endian flag for ext2 little-endian metadata conversion.
- `ext2_table`: fsdriver dispatch table.

Role:
- Connects all ext2 service modules through shared state.
- `group_descriptors_dirty` is particularly important for allocator updates and `write_super()`.
