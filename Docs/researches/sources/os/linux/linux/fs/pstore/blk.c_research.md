# File Research: sources/os/linux/linux/fs/pstore/blk.c

## Role

Implements the pstore block backend wrapper. It translates module/Kconfig sizing parameters into a `pstore_zone_info`, optionally opens a generic block device in best-effort mode, and registers the zone backend.

## Key Behavior

- Module parameters configure kmsg, pmsg, console, ftrace sizes, max kmsg reason, best-effort mode, and block device path.
- `__register_pstore_device()` validates a `pstore_device_info`, applies module parameter sizes, fills zone owner/name/max reason, and calls `register_pstore_zone()`.
- `register_pstore_device()` and `unregister_pstore_device()` export non-block device registration APIs under `pstore_blk_lock`.
- Best-effort block mode opens the configured block device with `O_RDWR | O_DSYNC | O_NOATIME | O_EXCL`, derives total size from `bdev_nr_bytes()`, and uses `kernel_read()`/`kernel_write()` callbacks.
- `psblk_generic_blk_write()` rejects interrupt or IRQ-disabled contexts because generic block writes are not panic-safe.

## Early Boot Handling

For built-in kernels, `early_boot_devpath()` resolves the configured block device using root-device lookup style logic, creates `/dev/pstore-blk`, and uses it before normal device nodes exist.

## Exports

- `register_pstore_device`
- `unregister_pstore_device`
- `pstore_blk_get_config`

## Research Notes

This backend's generic best-effort path is intentionally limited: without a dedicated panic write callback, it cannot safely write from interrupt/panic contexts. The actual persistence layout is delegated to `zone.c`.
