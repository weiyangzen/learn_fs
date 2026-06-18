# File Research: sources/virtualization/nbdkit/filters/fua/Makefile.am

Automake rules for `nbdkit-fua-filter.la`. Builds `fua.c` with the public filter header.

The build uses nbdkit include paths, warning CFLAGS, the Windows import library hook, module/shared libtool flags, and the optional common filter linker script. Man page generation is enabled through POD when available.
