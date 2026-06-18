# File Research: sources/virtualization/nbdkit/filters/xor/Makefile.am

This Automake file builds `nbdkit-xor-filter.la` from `xor.c` and the public filter header. It uses public/generated/common include paths and standard module linker flags, including the optional `filters/filters.syms` version script.

Unlike many filters, this module does not link common utility or replacement libraries; it only includes the platform import library variable. `nbdkit-xor-filter.pod` is distributed and conditionally converted to man/HTML documentation when POD support is enabled.

The build is unconditional and depends on helper headers from common include paths for alignment, min/max, random generation, and rounding.
