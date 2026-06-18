# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/Makefile.am

Automake rules for `nbdkit-indexed-gzip-filter.la`, gated by `HAVE_ZLIB`. Builds the filter glue plus zran-derived indexing files: `ig_handle.h`, `ig_zran.c`, `ig_zran.h`, `indexed_gzip.c`, `zran.c`, and `zran.h`.

Links zlib, math library, common utils, compatibility replacements, and the Windows import hook. Uses common nbdkit include paths and optional filter linker script. Builds the POD man page when POD tooling is available.
