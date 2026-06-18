# File Research: sources/virtualization/nbdkit/filters/gzip/Makefile.am

Automake rules for `nbdkit-gzip-filter.la`, gated by `HAVE_ZLIB`. Builds `gzip.c`.

Adds zlib CFLAGS and libraries, common utils, compatibility replacements, nbdkit include paths, Windows import hook, module/shared libtool flags, and optional filter linker script. POD man page generation is conditional on POD support.
