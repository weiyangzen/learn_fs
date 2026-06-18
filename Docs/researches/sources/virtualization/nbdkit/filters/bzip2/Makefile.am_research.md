# File Research: sources/virtualization/nbdkit/filters/bzip2/Makefile.am

Purpose: conditionally builds the bzip2 decompression filter.

Key details:
- Guarded by `HAVE_BZLIB`.
- Builds `nbdkit-bzip2-filter.la` from `bzip2.c`.
- Includes nbdkit headers, replacement headers, common includes, and utility headers.
- Links `BZLIB_LIBS`, `common/utils`, `common/replacements`, and Windows import support.
- Uses shared filter symbol script when enabled.
- Generates `nbdkit-bzip2-filter.1` from POD when `HAVE_POD`.

Risk notes:
- CFLAGS include `$(ZLIB_CFLAGS)` while linking `$(BZLIB_LIBS)`; this may be intentional carryover from gzip-like filters or a build variable mismatch worth checking.
