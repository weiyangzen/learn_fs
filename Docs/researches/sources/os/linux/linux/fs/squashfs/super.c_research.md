# File Research: sources/os/linux/linux/fs/squashfs/super.c

Implements SquashFS mount, unmount, statfs, fs context, and filesystem registration.

Mount options include `errors=continue|panic` and optional `threads=` selection/count. Defaults select the compile-time decompression mode.

`squashfs_fill_super()` sets block size, reads and validates the superblock, checks version/compressor/device bounds/block geometry/root inode/table ordering, initializes caches and decompressor stream, reads xattr/id/inode/fragment lookup tables, enables export ops when available, creates the root inode, and marks the filesystem read-only.

Unmount frees caches, page-cache mapping inode, decompressor stream, index tables, meta-index cache, and superblock private data.

Also defines inode slab allocation/free, `statfs`, show-options, fs context ops, filesystem type, module init/exit, and module metadata.
