# File Research: sources/os/darwin/xnu/bsd/vfs/Makefile

This 25-line make fragment participates in the XNU kernel build/export system for `bsd/vfs`.

It imports the shared XNU make definitions from `${SRCROOT}/makedefs` via `MakeInc.cmd`, `MakeInc.def`, `MakeInc.rule`, and `MakeInc.dir`. The only local data file named for install is `vfs_support.h`.

Export/install behavior:
- `INSTALL_MI_LIST`, `INSTALL_SF_MI_LCL_LIST`, and `INSTALL_KF_MI_LIST` all include `vfs_support.h`.
- `INSTALL_MI_DIR` is `vfs`.
- `EXPORT_MI_LIST` exports `vfs_support.h`, `vfs_disk_conditioner.h`, and `vfs_exclave_fs.h`.
- `EXPORT_MI_DIR` is also `vfs`.

This file contains no compilation rules of its own; it declares VFS public/support headers and delegates rule execution and directory traversal to the shared XNU make include files.
