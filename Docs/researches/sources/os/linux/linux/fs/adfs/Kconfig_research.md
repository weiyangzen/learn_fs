# File Research: sources/os/linux/linux/fs/adfs/Kconfig

Defines configuration for the Acorn Disc Filing System driver.

Key behavior:
- `ADFS_FS` is a tristate option depending on `BLOCK` and selecting `BUFFER_HEAD`.
- Help text describes read support for Acorn/RISC OS ADFS hard-drive partitions and floppy images.
- `ADFS_FS_RW` enables experimental write support and depends on `ADFS_FS`.
- Write support is explicitly labeled dangerous/experimental.

Important interactions:
- `ADFS_FS` controls whether `fs/adfs/` is built by the top-level `fs/Makefile`.
- Runtime write behavior in ADFS checks `CONFIG_ADFS_FS_RW`.
