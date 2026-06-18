# File Research: sources/virtualization/nbdkit/plugins/floppy/Makefile.am

Build definition for the floppy plugin.

Key contents:
- Distributed documentation: `nbdkit-floppy-plugin.pod`.
- Builds only when iconv support is available.
- Builds `nbdkit-floppy-plugin.la` from `directory-lfn.c`, `floppy.c`, `virtual-floppy.c`, and `virtual-floppy.h`.
- Includes nbdkit headers plus common regions, replacements, and utility headers.
- Links `libregions`, `libutils`, and optional Windows import library.
- Generates documentation with magic-parameter insertion when POD is available.
