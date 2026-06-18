# File Research: sources/os/linux/linux-stable/fs/cramfs/Kconfig

This file declares CramFs build options.

Key responsibilities:
- Defines `CONFIG_CRAMFS` as compressed ROM filesystem support and selects `ZLIB_INFLATE`.
- Defines `CONFIG_CRAMFS_BLOCKDEV` for block-device-backed images.
- Defines `CONFIG_CRAMFS_MTD` for directly mapped physical-memory/MTD images.

Dependencies:
- `CRAMFS_BLOCKDEV` depends on `CRAMFS && BLOCK`.
- `CRAMFS_MTD` depends on `CRAMFS && CRAMFS <= MTD`.

Risks and invariants:
- Help text documents CramFs as readonly, small, RAM-efficient, and intentionally limited.
- MTD mode supports `mount -t cramfs mtd:<name>`.
