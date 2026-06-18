# File Research: sources/os/linux/linux-stable/fs/pstore/blk.c

## Summary
Implements the pstore/blk backend wrapper. It accepts a registered pstore block-like device, normalizes module/Kconfig sizing, registers the device with pstore/zone, and optionally implements a best-effort generic block-device mode using `kernel_read()` and `kernel_write()`.

## Main Responsibilities
- Define module parameters for kmsg, pmsg, console, ftrace sizes, max dump reason, best-effort mode, and target block device.
- Validate `struct pstore_device_info` and populate its embedded `struct pstore_zone_info`.
- Register and unregister one pstore/blk device at a time.
- Provide exported `register_pstore_device()`, `unregister_pstore_device()`, and `pstore_blk_get_config()`.
- Implement generic block reads/writes for best-effort operation.
- Resolve early boot block device names for built-in best-effort mode.

## Key Interfaces
- `register_pstore_device()` registers a non-block or dedicated backend with pstore/zone.
- `unregister_pstore_device()` removes it.
- `pstore_blk_get_config()` reports normalized block backend configuration.
- `__register_pstore_blk()` opens a block device and sets `zone.total_size`.
- `psblk_generic_blk_read()` and `psblk_generic_blk_write()` are generic storage callbacks.

## Important Behavior
`verify_size()` converts configured KB sizes into bytes, clamps disabled frontends to zero, enforces alignment, updates module parameter values, and stores final values in `dev->zone`. If a backend supplies no frontend flags, it is treated as supporting all frontends.

Best-effort mode requires `best_effort=Y` and a nonempty `blkdev`. It opens the target with `O_RDWR | O_DSYNC | O_NOATIME | O_EXCL`, rejects non-block files, and registers the block size as the storage area. Its write path refuses interrupt or IRQ-disabled contexts, making it unsuitable for reliable panic persistence.

## State and Synchronization
`pstore_blk_lock` protects `psblk_file` and the single global `pstore_device_info`. Register/unregister paths assert this lock for internal helpers.

## Cross-File Interactions
This file is an adapter between external pstore block devices and `zone.c` via `register_pstore_zone()`. The core pstore frontend is still provided by `platform.c` and `inode.c`.

## Risks
The best-effort generic block path cannot write in panic/interrupt contexts and is explicitly weaker than a backend with a dedicated panic-safe write callback. Only one pstore/blk device may be registered globally.
