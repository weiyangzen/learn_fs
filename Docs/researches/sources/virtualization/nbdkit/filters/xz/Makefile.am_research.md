# File Research: sources/virtualization/nbdkit/filters/xz/Makefile.am

This Automake file builds the `nbdkit-xz-filter.la` module only when `HAVE_LIBLZMA` is true. The module sources are `blkcache.c`, `blkcache.h`, `xz.c`, `xzfile.c`, `xzfile.h`, and the public filter header.

The build includes public/generated nbdkit headers, common include files, and common utilities. It compiles with `$(LIBLZMA_CFLAGS)` and links `$(LIBLZMA_LIBS)`, common utilities, compatibility replacements, and the platform import library. The optional filter linker script is applied when configured.

`nbdkit-xz-filter.pod` is distributed. POD-enabled builds generate `nbdkit-xz-filter.1` and HTML documentation.
