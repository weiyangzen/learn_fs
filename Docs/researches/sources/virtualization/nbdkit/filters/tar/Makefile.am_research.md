# File Research: sources/virtualization/nbdkit/filters/tar/Makefile.am

This Automake file builds `nbdkit-tar-filter.la` from `tar.c` only on non-Windows platforms, because the implementation depends on `open_memstream` and shell/subprocess behavior. It distributes `nbdkit-tar-filter.pod`.

The module includes public/generated nbdkit headers, common include files, replacements, and utilities. It links against common utilities, compatibility replacements, and the Windows import library variable, although the module itself is guarded by `!IS_WINDOWS`. The optional filter linker version script is applied when available.

When POD support is present, it generates `nbdkit-tar-filter.1` and HTML documentation using `podwrapper.pl`.
