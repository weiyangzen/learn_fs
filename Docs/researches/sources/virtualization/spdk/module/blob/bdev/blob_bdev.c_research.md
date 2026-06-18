# File Research: sources/virtualization/spdk/module/blob/bdev/blob_bdev.c

Implements an `spdk_bs_dev` backend over an SPDK bdev.

Key elements:
- `struct blob_bdev` embeds `spdk_bs_dev` and tracks base bdev, descriptor, write mode, refs, and lock.
- Implements read/write, readv/writev, extended memory-domain I/O options, write zeroes, unmap, and copy.
- Queues failed `-ENOMEM` bdev submissions through `spdk_bdev_queue_io_wait()` and resubmits later.
- Handles bdev I/O completions by translating success to blobstore callback status.
- Implements channel creation/destruction using bdev I/O channels with refcounted lifetime.
- `spdk_bs_bdev_claim()` claims the bdev descriptor with read/write claim semantics.
- `spdk_bdev_create_bs_dev()` opens a named bdev and initializes the blobstore device wrapper.
- `spdk_bdev_update_bs_blockcnt()` refreshes blobstore-visible block count.

Dependencies:
- SPDK blobstore, bdev, bdev module, thread, endian, and logging APIs.

Research notes:
- Unmap is optional; if unsupported, it completes successfully because blobstore does not require unmap to zero data.
- Copy support is installed only when the base bdev supports `SPDK_BDEV_IO_TYPE_COPY`.
- Range validation asserts if CoW/esnap ranges exceed the underlying bdev.
