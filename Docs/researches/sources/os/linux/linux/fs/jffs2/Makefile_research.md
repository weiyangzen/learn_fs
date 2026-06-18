# File Research: sources/os/linux/linux/fs/jffs2/Makefile

## Role

This Makefile defines how the JFFS2 filesystem object is built and which source files are included under each Kconfig feature.

## Build Composition

The main object is:

- `obj-$(CONFIG_JFFS2_FS) += jffs2.o`

The base `jffs2-y` object includes core compression selection, directory/file operations, ioctl, node lists, allocation, read/write, node management, inode reading, scanning, garbage collection, symlink, build, erase, background GC, filesystem glue, writev, superblock, and debug code.

## Conditional Objects

Feature-dependent additions include:
- `wbuf.o` for `CONFIG_JFFS2_FS_WRITEBUFFER`.
- `xattr.o`, `xattr_trusted.o`, and `xattr_user.o` for `CONFIG_JFFS2_FS_XATTR`.
- `security.o` for `CONFIG_JFFS2_FS_SECURITY`.
- `acl.o` for `CONFIG_JFFS2_FS_POSIX_ACL`.
- `compr_rubin.o`, `compr_rtime.o`, `compr_zlib.o`, and `compr_lzo.o` for compressor options.
- `summary.o` for `CONFIG_JFFS2_SUMMARY`.

## Integration

This file is the compile-time bridge from Kconfig options to source modules. The files researched here map directly into this build:
- `build.o` and `background.o` are always included with JFFS2.
- `acl.o` is included only when POSIX ACL support is enabled.

## Research Notes

The Makefile confirms that mount/build and GC thread code are core JFFS2 behavior, while ACL support is optional and depends on the xattr/ACL configuration path.
