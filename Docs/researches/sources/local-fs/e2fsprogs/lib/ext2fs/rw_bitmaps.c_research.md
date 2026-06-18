# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/rw_bitmaps.c

Reads and writes block and inode bitmaps. Public helpers include `ext2fs_read_inode_bitmap`, `ext2fs_read_block_bitmap`, `ext2fs_read_bitmaps`, `ext2fs_write_inode_bitmap`, `ext2fs_write_block_bitmap`, and `ext2fs_write_bitmaps`.

Write paths serialize in-memory bitmaps to per-group bitmap blocks, force padding bits in the final block group, compute bitmap checksums, update group descriptor checksums, skip uninitialized groups when descriptor checksums permit, and clear dirty flags.

Read paths allocate bitmap structures, support e2image bitmap sources, verify bitmap checksums unless ignored, record bitmap tail padding problems, synthesize reserved metadata blocks for uninitialized block groups, and optionally use pthreads to read group ranges in parallel when the I/O channel supports threading.

External journal devices are rejected for bitmap operations. Threaded reads temporarily disable I/O caching and protect shared bitmap updates with a mutex.
