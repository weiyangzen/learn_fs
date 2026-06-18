# File Research: sources/os/linux/linux-stable/fs/romfs/Kconfig

Kconfig entries for ROMFS support.

Key options:
- `ROMFS_FS`: tristate read-only ROM filesystem, dependent on `BLOCK || MTD`.
- Backing-store choice:
  - `ROMFS_BACKED_BY_BLOCK`: block-device backed ROMFS, depends on `BLOCK`.
  - `ROMFS_BACKED_BY_MTD`: direct MTD backed ROMFS, depends on built-in or module-compatible MTD.
  - `ROMFS_BACKED_BY_BOTH`: enables both block and MTD backing.
- Derived booleans:
  - `ROMFS_ON_BLOCK`: selected when block or both backing is chosen; selects `BUFFER_HEAD`.
  - `ROMFS_ON_MTD`: selected when MTD or both backing is chosen.

Purpose:
- Lets small systems choose block, MTD, or both storage paths while keeping ROMFS read-only and compact.
