# File Research: sources/os/linux/linux/fs/omfs/Kconfig

Kconfig entry for the Linux OMFS filesystem driver.

Key contents:
- Defines `CONFIG_OMFS_FS` as a tristate option named “SonicBlue Optimized MPEG File System support”.
- Depends on `BLOCK`, because OMFS is mounted from block devices.
- Selects `BUFFER_HEAD`, matching the implementation’s buffer-head based metadata and block I/O.
- Selects `CRC_ITU_T`, used by inode/header checksum generation.
- Help text identifies OMFS as the proprietary filesystem used by Rio Karma and ReplayTV devices and notes the module name is `omfs`.
- Default guidance is conservative: say N if unsure.
