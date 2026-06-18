# File Research: sources/virtualization/qemu/block/block-ram-registrar.c

This file implements `BlockRAMRegistrar`, a helper that registers guest RAM blocks as block backend buffers when RAM blocks are added and unregisters them when removed.

Key behavior:
- `blk_ram_registrar_init()` stores the target `BlockBackend`, initializes a `RAMBlockNotifier`, sets `ok = true`, and registers the notifier.
- `ram_block_added()` calls `blk_register_buf()` for the new RAM block using `max_size`. On failure, it reports the error, removes the notifier, and marks the registrar failed so it will not retry.
- `ram_block_removed()` calls `blk_unregister_buf()` with the same host and max size.
- `blk_ram_registrar_destroy()` removes the notifier only if still active/ok.

Design note:
- Resize notifications are not needed because registration uses `max_size`, which does not change across resize.

Filesystem/block relevance:
- This supports block drivers that benefit from or require pre-registered guest memory, such as libblkio/virtio paths with registered buffers.
- It bridges QEMU RAM lifecycle events to block-backend buffer registration.

Potential pitfalls:
- A single registration failure permanently disables the registrar.
- Removal uses `max_size`, so register/unregister region derivation must remain consistent in lower block drivers.
