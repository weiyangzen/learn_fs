# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_fs.c

Implements optional virtio-fs over the common vfio-user virtio transport. It is compiled only when FSDEV support is enabled.

Key responsibilities:
- Registers the `virtio_fs` SPDK vfio-user endpoint model.
- Creates and owns an SPDK FUSE dispatcher for a configured fsdev.
- Exposes virtio-fs configuration, including tag and request queue count.
- Polls virtqueues and forwards FUSE requests to the dispatcher.
- Handles fsdev removal and asynchronous dispatcher deletion.
- Provides endpoint add function used by the RPC layer.

Important structures:
- `struct virtio_fs_endpoint`: embeds `vfu_virtio_endpoint`, FUSE dispatcher, init thread, I/O channel, virtio-fs config, destruction state, and ring poller.
- `struct virtio_fs_req`: wraps `vfu_virtio_req` and stores endpoint and status pointer fields.

Request handling:
- `virtio_fs_process_req()` validates that the first descriptor contains a `fuse_in_header`.
- It splits the request IOV array into input IOVs and output IOVs by summing input lengths until `fuse_in_header.len` is reached.
- Submits the request to `spdk_fuse_dispatcher_submit_request()`.
- Completion callback `virtio_fs_fuse_req_done()` finishes the virtio request with the negated FUSE error status.

Lifecycle:
- `vfu_virtio_fs_add_fsdev()` validates endpoint, fsdev name, and tag, sets queue options, fills `virtio_fs_config`, allocates async context, and creates the FUSE dispatcher.
- `virtio_fs_start()` gets the dispatcher I/O channel and registers the ring poller.
- `virtio_fs_stop()` sends a stop message to the endpoint thread to unregister the poller and release the channel.
- Destruction is asynchronous if a dispatcher still exists: it initiates dispatcher deletion and returns `-EAGAIN` until deletion completes.

Integration:
- Uses common virtio helpers for ring handling and PCI/vfio-user endpoint behavior.
- Uses `spdk_internal/fuse_dispatcher.h` and Linux FUSE/virtio-fs headers.
- Registers endpoint ops via constructor.
- Fills PCI device ID with `PCI_DEVICE_ID_VIRTIO_FS`.

Notes:
- `VIRTIO_FS_SUPPORTED_FEATURES` is currently zero beyond common host virtio features.
- The RPC layer marks virtio-fs vfio-user support as deprecated for removal in `v26.09`.
- The code includes a duplicated `spdk/stdinc.h` include, but it is harmless.
