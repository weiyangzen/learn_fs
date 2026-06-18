# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/checks.am

This Automake fragment defines the libgfs2 Check test program.

It sets:
- `TESTS = check_libgfs2`
- `check_PROGRAMS = $(TESTS)`

`check_libgfs2_SOURCES` combines the test runner and test files with the libgfs2 implementation files needed for a standalone test binary, including metadata, rgrp, CRC, disk hash, ondisk, buffer, geometry, fs ops, structures, bitmaps, misc, recovery, and superblock code.

It adds Check and uuid CFLAGS, and links against Check and uuid libraries.

This file is included from `Makefile.am` only when `HAVE_CHECK` is true.
