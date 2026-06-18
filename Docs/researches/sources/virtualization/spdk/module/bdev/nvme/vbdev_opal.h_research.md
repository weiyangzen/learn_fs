# File Research: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.h

This header declares the OPAL virtual bdev control API used by the OPAL RPC file. It includes bdev module support and the NVMe bdev private header so callers can reference NVMe controller names and OPAL bdev operations.

The exported functions create an OPAL locking-range bdev, query locking range info, destruct/delete an OPAL bdev, enable a new OPAL user, and set a locking range state. The APIs operate by bdev/controller names plus passwords and user/range IDs; implementation details and state structures remain private to `vbdev_opal.c`.

The header is Linux-build relevant because the Makefile includes OPAL sources only on Linux.
