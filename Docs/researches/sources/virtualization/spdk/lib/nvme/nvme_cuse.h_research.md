# File Research: sources/virtualization/spdk/lib/nvme/nvme_cuse.h

This small private header declares the internal CUSE registration interface used by the NVMe library.

It includes `spdk/nvme.h` for `struct spdk_nvme_ctrlr` and declares:

- `nvme_cuse_register(struct spdk_nvme_ctrlr *ctrlr, const char *dev_path)`
- `nvme_cuse_unregister(struct spdk_nvme_ctrlr *ctrlr)`

As read, these prototypes differ from the public functions implemented in `nvme_cuse.c`, which are named `spdk_nvme_cuse_register()` and `spdk_nvme_cuse_unregister()` and do not take a `dev_path`. This header may be stale or used by older integration code; any caller should be checked before relying on it.
