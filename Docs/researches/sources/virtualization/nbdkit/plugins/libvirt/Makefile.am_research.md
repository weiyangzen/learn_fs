# File Research: sources/virtualization/nbdkit/plugins/libvirt/Makefile.am

This Automake file builds the libvirt plugin when libvirt is available.

Key behavior:
- Gated by `HAVE_LIBVIRT`.
- Builds `nbdkit-libvirt-plugin.la` from `libvirt-plugin.c`.
- Adds nbdkit include paths and libvirt compiler flags.
- Links libvirt libraries and optional Windows import library.
- Uses module/shared flags and optional linker version script.
- Builds the man page when POD tooling is available.

Integration:
- This build target is separate from the `guestfs` plugin even though both can interact with libvirt domains.
