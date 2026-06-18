# File Research: sources/virtualization/nbdkit/plugins/full/Makefile.am

This Automake file builds and documents the `full` plugin.

Key behavior:
- Builds `nbdkit-full-plugin.la` from `full.c` and `nbdkit-plugin.h`.
- Adds include paths for source and build `include`.
- Links Windows import library when needed.
- Uses module/shared libtool flags and optional linker version script.
- If POD tooling is available, builds `nbdkit-full-plugin.1` from the POD source and inserts the magic-parameter documentation snippet.

Integration:
- The plugin is unconditional in this file, unlike plugins gated on external dependencies.
- Documentation generation follows the standard nbdkit plugin pattern.
