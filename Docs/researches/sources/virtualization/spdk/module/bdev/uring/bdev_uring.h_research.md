# File Research: sources/virtualization/spdk/module/bdev/uring/bdev_uring.h

Header for the uring bdev module.

Defines:
- Async delete callback `spdk_delete_uring_complete`.
- `struct bdev_uring_opts` with name, filename, block size, and UUID.
- `create_uring_bdev()`, `delete_uring_bdev()`, and `bdev_uring_rescan()`.

Used by RPC code and module consumers.
