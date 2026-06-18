# File Research: sources/os/linux/linux/fs/hpfs/Kconfig

Purpose: Defines the Linux HPFS filesystem configuration option.

Key content:
- `config HPFS_FS` is a tristate option named “OS/2 HPFS file system support”.
- Depends on `BLOCK`.
- Selects `BUFFER_HEAD` and `FS_IOMAP`.
- Help text describes OS/2/Warp HPFS read/write support and module name `hpfs`.

Dependencies and integration:
- Enables compilation of the HPFS filesystem under `fs/hpfs`.

Risk notes:
- HPFS is block-device-only and buffer-head/iomap dependent.
