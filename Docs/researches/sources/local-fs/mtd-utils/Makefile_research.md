# File Research: sources/local-fs/mtd-utils/Makefile

## Purpose
Top-level build script for this vendored `mtd-utils` tree, version `1.5.2`.

## Key Elements
Declares top-level MTD utilities, UBI utilities, `mkfs.ubifs`, static libraries, and installed scripts. Generates `include/version.h`, includes `common.mk`, and defines object/library relationships for `mkfs.jffs2`, `lib/libmtd.a`, `mkfs.ubifs`, and `ubi-utils` libraries.

## Dependencies
Uses zlib, optional LZO, UUID libraries, `ubi-utils`, `mkfs.ubifs`, local `include`, and `lib/libmtd.a`. Build toggles include `WITHOUT_XATTR`, `WITHOUT_LZO`, and externally supplied `ZLIB*`, `LZO*`, `UUID*` flags.

## Behavior/Risks
The `install` target installs all binaries/scripts to `${DESTDIR}/${SBINDIR}` and gzips man pages. `clean` conditionally removes `$(BUILDDIR)`, guarded to avoid deleting the source directory, but still expects make variables to be correct.
