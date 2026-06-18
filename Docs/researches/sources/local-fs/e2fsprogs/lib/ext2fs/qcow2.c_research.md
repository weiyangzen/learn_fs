# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.c

Provides qcow2-to-raw image conversion helpers. `qcow2_read_header()` reads and validates qcow2 magic/version, and `qcow2_write_raw_image()` walks qcow2 metadata to copy allocated clusters to a raw output file.

The converter rejects encrypted images, compressed clusters, invalid cluster bit ranges, unaligned L1 table offsets, and oversized L1 tables. It reads the L1 table, then each referenced L2 table, then copies non-zero cluster entries to the corresponding raw offset.

The raw output is resized by seeking to `image_size - 1` and writing one zero byte. The implementation is intentionally limited: it does not implement qcow2 compression, snapshots, refcount validation, or writes back to qcow2.
