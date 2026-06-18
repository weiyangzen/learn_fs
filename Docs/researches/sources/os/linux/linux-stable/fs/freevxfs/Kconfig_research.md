# File Research: sources/os/linux/linux-stable/fs/freevxfs/Kconfig

This Kconfig entry defines the build option for the FreeVxFS filesystem driver.

Major responsibilities:
- Declares `CONFIG_VXFS_FS` as a tristate option named "FreeVxFS file system support".
- Requires block-device support through `depends on BLOCK`.
- Selects `BUFFER_HEAD`, matching the driver's buffer-head based read path.
- Documents the driver as read-only support for VERITAS VxFS-compatible filesystems.
- Notes tested compatibility with SCO UnixWare and HP-UX VxFS variants.
- Clarifies that the mount filesystem type is `vxfs` even though the module is `freevxfs`.

Important design points:
- The help text explicitly frames the driver as format compatibility, not full vendor VxFS functionality.
- It calls out version support for VxFS 2, 3, and 4.
- It warns that OS-specific VxFS implementations may differ by endianness and superblock offset, which matches the superblock probing code.

Key invariants:
- The driver is not a write-capable filesystem.
- The module name and mount type differ: module `freevxfs`, filesystem type `vxfs`.

External interfaces:
- Produces `CONFIG_VXFS_FS`, used by the Makefile and build system.
