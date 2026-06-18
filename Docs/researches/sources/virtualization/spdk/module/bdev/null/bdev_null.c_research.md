# File Research: sources/virtualization/spdk/module/bdev/null/bdev_null.c

This file implements SPDK's synthetic null bdev module. It registers the `null` bdev module, creates/destroys in-memory bdev descriptors, completes accepted I/O asynchronously through a per-channel poller, exports JSON config, and supports runtime resize.

The module state is a global tailq of `struct null_bdev` plus a single DMA zero buffer used when read callers did not supply an iov base. Each I/O channel owns a poller and a queue of pending `null_bdev_io` contexts. `submit_request` validates and queues read, write, write-zeroes, and reset operations; the poller swaps the channel queue into a local list and completes each I/O with success. Abort is handled synchronously by searching the channel pending queue, removing the target, and completing it as aborted.

Read and write paths integrate optional DIF. Reads generate DIF into the returned buffer, while writes verify DIF and fail on mismatch with detailed error logging. Creation validates supported metadata sizes, 512-byte alignment for data and physical block sizes, nonzero block count, and DIF configuration through a dummy DIF context. The exported bdev block length includes metadata size because metadata is interleaved.

The JSON config writer serializes `bdev_null_create` parameters, including UUID, DIF, physical block size, preferred write/unmap hints, and geometry. `bdev_null_resize()` opens the bdev, verifies it belongs to this module, rejects shrinking, and updates block count through `spdk_bdev_notify_blockcnt_change()`.

Important invariants are that the shared read buffer is bounded by `SPDK_BDEV_LARGE_BUF_MAX_SIZE`, queued I/O must be removed before completion, destruct removes the bdev from the global tailq and frees the name, and module finalization unregisters the io_device before freeing `g_null_read_buf`.
