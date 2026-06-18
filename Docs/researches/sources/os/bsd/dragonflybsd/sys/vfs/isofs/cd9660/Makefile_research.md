# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/Makefile

Source read: complete file, 10 lines.

Purpose: Kernel module makefile for the cd9660 ISO 9660 filesystem.

Key contents:
- Sets `KMOD= cd9660`.
- Builds `cd9660_bmap.c`, `cd9660_lookup.c`, `cd9660_node.c`, `cd9660_rrip.c`, `cd9660_util.c`, `cd9660_vfsops.c`, and `cd9660_vnops.c`.
- Exports `cd9660_iconv`.
- Builds `cd9660_iconv` as a subdirectory module.
- Includes `<bsd.kmod.mk>`.

Integration:
- The files in this group are a subset of the module sources; lookup and bmap depend on node, util, RRIP, VFS, and vnode code in neighboring files.

Risks and review notes:
- `EXPORT_SYMS= cd9660_iconv` is important for the iconv support module and VFS code to share the conversion hook.
