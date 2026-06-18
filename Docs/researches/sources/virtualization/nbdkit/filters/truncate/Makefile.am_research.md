# File Research: sources/virtualization/nbdkit/filters/truncate/Makefile.am

This Automake file builds `nbdkit-truncate-filter.la` from `truncate.c` and the public filter header. It uses standard nbdkit filter module flags, common include paths, common utility/replacement libraries, the platform import library, and the optional `filters/filters.syms` linker script.

The POD file `nbdkit-truncate-filter.pod` is distributed. When POD support is enabled, `podwrapper.pl` generates the section 1 man page and HTML output.

The build is unconditional across supported platforms, relying only on common nbdkit helpers such as rounding, zero detection, and power-of-two validation.
