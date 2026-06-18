# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/Makefile.am

This Automake fragment builds the internal `libgfs2.la` library and the `gfs2l` helper program.

Key build declarations:
- Generated parser/lexer files are cleaned and partially treated as built sources.
- `_GNU_SOURCE` and uuid CFLAGS are added globally.
- Internal headers include `libgfs2.h`, `crc32c.h`, `lang.h`, and `rgrp.h`.
- `libgfs2_la_SOURCES` include core filesystem logic: CRC, bitmap, misc, rgrp, superblock, buffers, disk hash, ondisk conversion, geometry, fs ops, recovery, structures, and metadata.
- `gfs2l` is built from language/parser sources and links `libgfs2.la` plus uuid.
- `lexer.h` is generated manually from `lexer.l`.
- `checks.am` is included only when `HAVE_CHECK` is enabled.

This file controls the library surface consumed by fsck, mkfs, glocktop, and tests.
