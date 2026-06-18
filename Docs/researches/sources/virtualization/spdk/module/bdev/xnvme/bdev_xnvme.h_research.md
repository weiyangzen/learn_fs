# File Research: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.h

Header for xNVMe bdev control.

Declares:
- `create_xnvme_bdev(name, filename, io_mechanism, conserve_cpu)`.
- `delete_xnvme_bdev(name, cb_fn, cb_arg)`.

Used by the xNVMe RPC implementation.
