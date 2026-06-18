# File Research: sources/os/linux/linux/fs/ntfs3/Kconfig

Read coverage: complete file, 49 lines.

This Kconfig file defines build-time options for the newer Paragon `ntfs3` driver.

Options:
- `NTFS3_FS`: tristate NTFS read-write filesystem support for filesystem type/module `ntfs3`; selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`; depends on the legacy `NTFS_FS` not being built-in unless `ntfs3` is modular.
- `NTFS3_64BIT_CLUSTER`: optional 64-bit cluster support on 64-bit builds; warns that Windows cannot mount such volumes and recommends `N`.
- `NTFS3_LZX_XPRESS`: enables reading Windows 10 external compression formats xpress4k/xpress8k/xpress16k/lzx; recommends `Y`.
- `NTFS3_FS_POSIX_ACL`: enables Linux-only POSIX ACL support and selects `FS_POSIX_ACL`; recommends `N` if unsure.

Integration:
- Controls compilation paths in `Makefile` and conditional code such as WOF/LZX/XPRESS support.

Risk:
- Feature toggles change on-disk interoperability, especially 64-bit clusters and Linux-only ACLs.
