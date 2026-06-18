# File Research: sources/virtualization/spdk/module/bdev/ocf/data.h

This header defines `struct bdev_ocf_data`, the OCF data wrapper used in bdev I/O contexts. It stores an iovec pointer, current iovec count, allocated capacity, total size, and seek position.

It declares helpers to allocate/free data wrappers, map from `spdk_bdev_io`, append iovs, and a prototype for `vbdev_ocf_data_from_iov()`. In this file group, `vbdev_ocf_data_from_iov()` is declared but not implemented in `data.c`, so callers should be checked before relying on it.

The structure is shared with `ctx.c`, where OCF data callbacks use `size`, `seek`, and the iovec array to read, write, zero, copy, and securely erase data.
