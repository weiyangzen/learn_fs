# File Research: sources/virtualization/libblockdev/src/utils/blockdev-utils.pc.in

This is the pkg-config template for `libbd_utils`.

Fields:
- Defines `prefix`, `exec_prefix`, `includedir`, and `libdir`.
- `Name: BlockDev-utils`
- Describes the library as utility functions used by libblockdev.
- Points to `https://github.com/storaged-project/libblockdev`.
- Uses `@VERSION@`.
- Requires `glib-2.0`.
- Exposes `-L${libdir} -lbd_utils`.
- Exposes `-I${includedir}`.

Research relevance:
- External consumers can compile/link against the utility library independently through pkg-config.
