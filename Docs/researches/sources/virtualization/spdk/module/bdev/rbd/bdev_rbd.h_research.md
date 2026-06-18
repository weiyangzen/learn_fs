# File Research: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.h

Public/internal header for the RBD bdev module and its RPC front-end.

Defines:
- `struct cluster_register_info`: cluster name, user, config parameters, config/key files, and optional core mask.
- Config helpers `bdev_rbd_free_config()` and `bdev_rbd_dup_config()`.
- Async delete callback type `spdk_delete_rbd_complete`.
- Public module functions for create, delete, resize, register/unregister cluster, and emit cluster info.

This header is the interface boundary between `bdev_rbd.c` and `bdev_rbd_rpc.c`.
