# File Research: sources/os/linux/linux/block/fops.c

Implements the default file operations for block special files, including open/release, direct and buffered read/write, mmap preparation, fsync, fallocate, and io_uring command entry.

Key responsibilities:
- Converts file flags to `blk_mode_t` with `file_to_blk_mode()`.
- Opens block devices through `bdev_permission()`, `blkdev_get_no_open()`, and `bdev_open()`.
- Implements direct I/O using bios, including simple inline-bvec, async single-bio, and multi-bio paths.
- Handles buffered I/O through iomap or buffer-head based address-space operations depending on `CONFIG_BUFFER_HEAD`.
- Enforces block-size alignment for direct I/O.
- Truncates reads/writes at device size and rejects writes past end.
- Blocks writes to read-only devices and active swap devices except hibernate resume devices.
- Implements fallocate zero/punch/write-zeroes over block-device ranges.

Important functions:
- `blkdev_direct_IO()`, `__blkdev_direct_IO_simple()`, `__blkdev_direct_IO_async()`, `__blkdev_direct_IO()` build and submit bio-based direct I/O.
- `blkdev_read_iter()` and `blkdev_write_iter()` are the main file data paths.
- `blkdev_fsync()` flushes the block device and treats unsupported flush as success.
- `blkdev_fallocate()` validates flags/ranges and issues zeroout/write-zeroes.
- `def_blk_fops` exports the default block-device `file_operations`.
- `def_blk_aops` exports the block-device address-space operations.
- `blkdev_init()` initializes the direct-I/O bioset.

Concurrency/lifetime notes:
- Buffered I/O takes `inode_lock_shared()` to avoid races with block size changes and page-cache invalidation.
- Direct write invalidates cached pages before and after I/O.
- Async direct I/O stores private state in bioset-backed `struct blkdev_dio` and completes via kiocb callbacks.
- Polling direct I/O stores the bio in `iocb->private`.

Research relevance:
- This is the user-visible block special file data path, tying VFS I/O to bio submission.
