# File Research: sources/virtualization/nbdkit/plugins/blkio/Makefile.am

This Automake file builds `nbdkit-blkio-plugin.la` only when `HAVE_LIBBLKIO` is true. The module source is `blkio.c` plus the public plugin header.

The build uses public/generated headers, common include files, and common utilities. It compiles with `$(LIBBLKIO_CFLAGS)` and links common utilities, the platform import library, and `$(LIBBLKIO_LIBS)`. Standard plugin module flags and the optional `plugins/plugins.syms` version script are applied.

The POD file `nbdkit-blkio-plugin.pod` is distributed. POD generation inserts the shared magic-parameter text before building the man page and HTML output.
