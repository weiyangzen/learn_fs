# File Research: sources/virtualization/nbdkit/plugins/guestfs/Makefile.am

This Automake file builds the libguestfs-backed plugin when libguestfs is available.

Key behavior:
- Gated by `HAVE_LIBGUESTFS`.
- Builds `nbdkit-guestfs-plugin.la` from `guestfs-plugin.c`.
- Adds include paths for nbdkit headers and common utilities.
- Links `libutils`, Windows import library if needed, and `LIBGUESTFS_LIBS`.
- Uses module/shared libtool flags and optional linker version script.
- Builds the man page when POD tooling is available.

Integration:
- Dependency gating prevents building when libguestfs development files are absent.
