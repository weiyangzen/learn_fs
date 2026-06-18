# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/Makefile.am

This Automake file builds the Linux virtual disk plugin when `mke2fs -d` support is available and the platform is not Windows.

Key behavior:
- Gated by `HAVE_MKE2FS_WITH_D` and `!IS_WINDOWS`.
- Builds `nbdkit-linuxdisk-plugin.la` from filesystem, plugin, GPT, virtual disk, and header files.
- Includes common GPT, regions, utils, and nbdkit headers.
- Links `libgpt`, `libregions`, `libutils`, and optional Windows import library.
- Uses optional linker version script.
- Builds the man page when POD tooling is available.

Integration:
- The plugin depends on external `mke2fs` behavior as well as in-tree GPT and region helpers.
