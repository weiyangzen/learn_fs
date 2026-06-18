# File Research: sources/virtualization/spdk/module/bdev/aio/bdev_aio.h

This header exposes the AIO bdev management API used by the RPC layer. It declares `create_aio_bdev()` with name, filename, block size, readonly, fallocate, UUID, and nowait parameters; `bdev_aio_rescan()` for backing-size refresh and detach detection; and asynchronous deletion via `bdev_aio_delete()`.

Deletion uses a `delete_aio_bdev_complete` callback carrying a bdev errno. The implementation details of file descriptors, AIO contexts, and IO channels are intentionally private to `bdev_aio.c`.
