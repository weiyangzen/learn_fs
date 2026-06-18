# File Research: sources/os/linux/linux/fs/romfs/Kconfig

## Purpose
Defines Kconfig options for Linux ROMFS support and its backing-store choices.

## Main Configuration
- `ROMFS_FS`
  - Tristate option: "ROM file system support".
  - Depends on `BLOCK || MTD`.
  - Builds module named `romfs` when selected as module.
  - Described as a small read-only filesystem for init/install media and other read-only storage.

## Backing Store Choice
The `choice` block is visible when `ROMFS_FS` is enabled:
- `ROMFS_BACKED_BY_BLOCK`
  - Block-device backed ROMFS.
  - Depends on `BLOCK`.
  - Uses page-cache/block buffering and does not support direct mapping.
- `ROMFS_BACKED_BY_MTD`
  - MTD-backed ROMFS.
  - Depends on built-in MTD or module-compatible MTD.
  - Supports direct MTD access and, under NOMMU, direct mapping when CPU-addressable.
- `ROMFS_BACKED_BY_BOTH`
  - Enables both block and MTD paths.
  - Depends on both block support and compatible MTD support.

## Derived Options
- `ROMFS_ON_BLOCK`
  - Internal bool.
  - Defaults to `y` for block or both.
  - Selects `BUFFER_HEAD`.
- `ROMFS_ON_MTD`
  - Internal bool.
  - Defaults to `y` for MTD or both.

## Research Notes
This file controls which code paths in `storage.c` and `mmap-nommu.c` are compiled. The build requires at least one backing-store interface, enforced again by `storage.c`.
