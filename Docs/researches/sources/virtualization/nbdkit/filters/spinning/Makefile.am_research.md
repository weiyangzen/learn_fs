# File Research: sources/virtualization/nbdkit/filters/spinning/Makefile.am

This Automake file builds the `nbdkit-spinning-filter.la` module from `spinning.c` and the public filter header. It installs the filter as a libtool module with `-module -avoid-version -shared`, applies the shared Windows no-undefined/import-library handling, and optionally applies `filters/filters.syms` as a linker version script.

Include paths cover generated headers, public nbdkit headers, common utilities, and common include files. The filter links against `common/utils/libutils.la`, `common/replacements/libcompat.la`, the Windows import library when applicable, and `-lm` for math functions used in the seek-time curve.

The file also distributes `nbdkit-spinning-filter.pod` and conditionally builds the man page and HTML documentation via `podwrapper.pl` when POD support is available.
