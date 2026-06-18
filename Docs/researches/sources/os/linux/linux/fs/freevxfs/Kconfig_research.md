# File Research: sources/os/linux/linux/fs/freevxfs/Kconfig

Read status: complete, 27 lines.

Purpose: declares `CONFIG_VXFS_FS` for FreeVxFS support.

Content:
- `tristate "FreeVxFS file system support (VERITAS VxFS(TM) compatible)"`.
- Depends on `BLOCK` and selects `BUFFER_HEAD`.
- Documents read-only support for VxFS versions 2, 3, and 4, with tested SCO UnixWare and HP-UX variants.
- Module name is `freevxfs`; mount filesystem type is `vxfs`.

Integration note: this config enables the read-only block-device filesystem driver built by the adjacent Makefile.
