# File Research: sources/virtualization/nbdkit/filters/lzip/Makefile.am

Automake rules for `nbdkit-lzip-filter.la`, gated by `HAVE_LZMA_LZIP_DECODER`.

Builds `lzip.c`, `lzipfile.c`, `lzipfile.h`, `lzipindex.c`, `lzipindex.h`, plus a symlinked `blkcache.c` from the xz filter and the xz `blkcache.h`. The symlink workaround exists because old Automake/subdir-objects behavior was problematic.

Uses liblzma CFLAGS/libs, common utils, compatibility replacements, nbdkit and xz include paths, Windows import hook, module/shared flags, and optional filter linker script. POD man page generation is conditional.
