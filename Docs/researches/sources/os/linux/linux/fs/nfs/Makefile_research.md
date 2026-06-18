# File Research: sources/os/linux/linux/fs/nfs/Makefile

Build rules for the Linux NFS client.

Key behavior:
- Builds `nfs.o` when `CONFIG_NFS_FS` is enabled.
- Core NFS object list includes client, dir, file, inode, super, I/O, direct I/O, pagelist, read/write, namespace, mount client, trace, export, sysfs, and fs_context code.
- Adds optional objects:
  - `nfsroot.o` for `CONFIG_ROOT_NFS`.
  - `sysctl.o` for `CONFIG_SYSCTL`.
  - `fscache.o` for `CONFIG_NFS_FSCACHE`.
  - `localio.o` for `CONFIG_NFS_LOCALIO`.
- Builds separate modules/objects for NFSv2, NFSv3, and NFSv4.
- Adds layout subdirectories:
  - `filelayout/`
  - `blocklayout/`
  - `flexfilelayout/`

Role:
- Wires NFS fscache integration and pNFS block layout into kernel build based on Kconfig.
