# File Research: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme_rpc.c

## Purpose
Registers JSON-RPC methods for xNVMe-backed bdevs.

## RPCs
- `bdev_xnvme_create`: decodes name, filename, I/O mechanism, optional conserve-CPU flag, calls `create_xnvme_bdev()`, returns name.
- `bdev_xnvme_delete`: decodes name and unregisters asynchronously.

Create failures are returned as generic internal errors. Delete callback returns boolean success or backend errno.
