# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/Makefile

Kernel module build descriptor for the DragonFly UDF filesystem.

Key responsibilities:
- Declares the kernel module name as `udf`.
- Builds the module from `osta.c`, `udf_vfsops.c`, and `udf_vnops.c`.
- Includes DragonFly's common kernel-module make rules through `bsd.kmod.mk`.

Dependencies:
- Requires the kernel build system's `bsd.kmod.mk`.
- The source list must remain synchronized with the UDF implementation files.

Notable risks:
- Adding UDF support code without updating `SRCS` would silently exclude it from the module build.
- This module is read-only at VFS registration time, so write-support files would also need VFS flag changes elsewhere.
