# File Research: sources/virtualization/nbdkit/filters/swab/Makefile.am

This Automake file builds the `nbdkit-swab-filter.la` module from `swab.c` and the public filter header. It uses the shared nbdkit module flags, optional linker version script, and links against common utilities, compatibility replacements, and the Windows import library where applicable.

Include paths cover public/generated nbdkit headers plus common include and utility directories. `nbdkit-swab-filter.pod` is included in `EXTRA_DIST`, and POD-enabled builds generate the `nbdkit-swab-filter.1` manual page and corresponding HTML.

The build file has no platform guard beyond the common Windows import/no-undefined handling, so the filter is intended to be broadly portable.
