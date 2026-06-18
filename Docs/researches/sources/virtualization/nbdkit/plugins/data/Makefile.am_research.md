# File Research: sources/virtualization/nbdkit/plugins/data/Makefile.am

Automake build definition for `nbdkit-data-plugin`.

Key contents:
- Builds `nbdkit-data-plugin.la` from `data.c`, `data.h`, `format.c`, and `format.h`.
- Distributes `disk2data.pl` and `nbdkit-data-plugin.pod`.
- Includes nbdkit headers plus common allocator, replacement, and utility directories.
- Links against `liballocators`, `libutils`, compatibility library, optional import library, and GnuTLS.
- Generates man/html documentation when POD support is available.
