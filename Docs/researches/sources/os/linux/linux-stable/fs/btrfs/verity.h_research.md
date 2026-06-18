# File Research: sources/os/linux/linux-stable/fs/btrfs/verity.h

## Scope

This header declares Btrfs fs-verity integration points and provides stubs when fs-verity is disabled.

## APIs

- Under `CONFIG_FS_VERITY`, declares `btrfs_verityops`, `btrfs_drop_verity_items()`, and `btrfs_get_verity_descriptor()`.
- Without fs-verity, `btrfs_drop_verity_items()` returns success and `btrfs_get_verity_descriptor()` returns `-EPERM`.

## Dependencies And Role

- Includes `<linux/fsverity.h>` only when fs-verity support is enabled.
- Keeps callers buildable regardless of the fs-verity Kconfig setting.

## Risks And Invariants

- Disabled-build stubs intentionally do not expose descriptor data.
- Callers must account for `-EPERM` from `btrfs_get_verity_descriptor()` when fs-verity is not compiled in.
