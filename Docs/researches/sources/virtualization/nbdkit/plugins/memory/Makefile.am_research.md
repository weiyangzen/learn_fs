# File Research: sources/virtualization/nbdkit/plugins/memory/Makefile.am

This Automake file builds the in-memory block device plugin.

Key behavior:
- Builds `nbdkit-memory-plugin.la` from `memory.c`.
- Includes allocator, replacement, utility, and nbdkit headers.
- Links allocator, compat, utils, and optional Windows import libraries.
- Uses module/shared flags and optional linker version script.
- Builds `nbdkit-memory-plugin.1` with magic-parameter insertion when POD tooling is available.

Integration:
- Runtime allocator behavior is supplied by the common allocator library.
