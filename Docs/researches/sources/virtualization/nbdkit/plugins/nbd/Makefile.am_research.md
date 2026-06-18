# File Research: sources/virtualization/nbdkit/plugins/nbd/Makefile.am

This Automake file builds the nbd proxy/client plugin when libnbd is available.

Key behavior:
- Gated by `HAVE_LIBNBD`.
- Builds `nbdkit-nbd-plugin.la` from `nbd.c` and nbdkit headers.
- Includes common headers, utils, and server headers.
- Uses libnbd compiler/linker flags.
- Links common utils, optional Windows import library, and `LIBNBD_LIBS`.
- Uses module/shared flags and optional linker version script.
- Builds `nbdkit-nbd-plugin.1` with magic-parameter documentation insertion when POD tooling is available.

Integration:
- This file only covers build wiring; the runtime implementation is in `nbd.c`, which was not part of this work item.
