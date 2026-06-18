# File Research: sources/local-fs/xfsdump/m4/Makefile

Build-system Makefile for m4/autoconf macro files.

Key details:
- Lists libtool macro files in `CONFIGURE`.
- Lists package-specific m4 files in `LSRCFILES`.
- Default target does nothing beyond build-rule integration.
- `realclean` depends on `distclean` and removes generated libtool macro files.

Role:
- Maintains macro source distribution and cleanup behavior.
