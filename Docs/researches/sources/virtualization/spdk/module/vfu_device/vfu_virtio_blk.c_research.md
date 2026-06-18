# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_blk.c

Implements the virtio-blk device model over the common vfio-user virtio transport.

Key responsibilities:
- Registers the `virtio_blk` SPDK vfio-user endpoint model.
- Opens an SPDK bdev and exposes it as a virtio-blk PCI device.
- Builds `virtio_blk_config` from bdev capacity, block size, queue count, topology, discard, write-zeroes, and flush capabilities.
- Polls virtqueues and dispatches block requests to SPDK bdev I/O.
- Handles bdev remove and resize events.
- Provides device feature bits and device-specific configuration reads.

Important structures:
- `struct virtio_blk_endpoint`: embeds `vfu_virtio_endpoint`, bdev descriptor, bdev pointer, I/O channel, virtio block config, init thread, and ring poller.
- `struct virtio_blk_req`: wraps `vfu_virtio_req` and stores the response status byte pointer and endpoint pointer.

Request handling:
- `virtio_blk_process_req()` validates the request header and response status descriptor.
- Supports:
  - `VIRTIO_BLK_T_IN`: `spdk_bdev_readv()`
  - `VIRTIO_BLK_T_OUT`: `spdk_bdev_writev()`
  - `VIRTIO_BLK_T_DISCARD`: `spdk_bdev_unmap()`
  - `VIRTIO_BLK_T_WRITE_ZEROES`: `spdk_bdev_write_zeroes()`
  - `VIRTIO_BLK_T_FLUSH`: `spdk_bdev_flush()`
  - `VIRTIO_BLK_T_GET_ID`: copies the bdev name padded to the virtio block ID field
- Completes requests through `blk_request_complete_cb()` or immediate status completion.
- Sets `req->used_len` according to virtio-blk direction and response semantics.

Lifecycle:
- `vfu_virtio_blk_add_bdev()` finds an existing vfio-user endpoint, sets queue options, opens the bdev, updates config, and records the init thread.
- `virtio_blk_start()` gets the bdev I/O channel and registers the virtqueue poller.
- `virtio_blk_stop()` sends a stop message to the endpoint thread to unregister the poller and release the I/O channel.
- Endpoint destruct closes the bdev descriptor on the init thread, destructs common virtio endpoint state, and frees the endpoint.

Integration:
- Uses common virtio helpers for ring polling and request completion.
- Uses SPDK bdev APIs for all storage I/O.
- Registers endpoint ops in a constructor via `spdk_vfu_register_endpoint_ops(&vfu_virtio_blk_ops)`.
- Fills PCI device ID with `PCI_DEVICE_ID_VIRTIO_BLK_MODERN`.

Notes:
- Payload length must be nonzero and 512-byte aligned for read/write commands.
- Bdev removal zeroes config, stops the device if active, closes the descriptor asynchronously, and causes later requests to fail with I/O error.
