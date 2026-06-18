# File Research: sources/virtualization/spdk/lib/nvme/nvme_io_msg.h

This private header declares the NVMe external I/O message bridge.

It defines `spdk_nvme_io_msg_fn`, a callback taking controller, NSID, and opaque argument. `struct spdk_nvme_io_msg` stores one queued callback invocation. `struct nvme_io_msg_producer` names a producer and provides `update()` and `stop()` hooks, linked through the controller’s producer list.

The declared functions are `nvme_io_msg_send()`, `nvme_io_msg_process()`, `nvme_io_msg_ctrlr_register()`, `nvme_io_msg_ctrlr_unregister()`, `nvme_io_msg_ctrlr_detach()`, and `nvme_io_msg_ctrlr_update()`.

The header documents the central contract: `nvme_io_msg_process()` is nonblocking, must be polled by an SPDK thread, and each controller must be polled by only one thread at a time. This is what makes external ioctl-style producers safe to integrate with SPDK NVMe request completion.
