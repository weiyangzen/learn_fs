# File Research: sources/virtualization/nbdkit/plugins/zero/Makefile.am

Builds the always-available `zero` plugin.

Key behavior:
- Distributes `nbdkit-zero-plugin.pod`.
- Builds `nbdkit-zero-plugin.la` from `zero.c` and the public plugin header.
- Adds source/build include directories.
- Links as a libtool module with Windows no-undefined/import support.
- Adds plugin linker script when enabled.
- Generates `nbdkit-zero-plugin.1` from POD when POD support is enabled.

Dependencies:
- nbdkit plugin API.
- Standard automake/libtool infrastructure.
