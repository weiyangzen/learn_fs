# File Research: sources/os/linux/linux-stable/fs/ntfs3/Kconfig

This file defines Linux Kconfig options for the newer `ntfs3` driver.

Main responsibilities:
- Defines `NTFS3_FS`, a tristate read-write NTFS filesystem driver option.
- Ensures `ntfs3` does not conflict with built-in legacy `NTFS_FS` by depending on `!NTFS_FS || m`.
- Selects required kernel features: `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`.
- Exposes optional 64-bit cluster support through `NTFS3_64BIT_CLUSTER`.
- Exposes optional Windows 10 external compression support through `NTFS3_LZX_XPRESS`.
- Exposes POSIX ACL support through `NTFS3_FS_POSIX_ACL`, selecting `FS_POSIX_ACL`.

Research notes:
- The main help text describes read/write support, journal replay, sparse/compressed file support, mount type `ntfs3`, and module name `ntfs3`.
- `NTFS3_64BIT_CLUSTER` is explicitly documented as not Windows-compatible for such volumes.
