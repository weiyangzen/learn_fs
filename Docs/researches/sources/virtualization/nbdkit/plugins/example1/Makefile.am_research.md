# File Research: sources/virtualization/nbdkit/plugins/example1/Makefile.am

Build definition for the minimal C example plugin.

Key contents:
- Builds `nbdkit-example1-plugin.la` from `example1.c`.
- Includes nbdkit headers only.
- Links optional Windows import library.
- Adds linker version script when enabled.
- Generates man/html documentation from POD when available.
