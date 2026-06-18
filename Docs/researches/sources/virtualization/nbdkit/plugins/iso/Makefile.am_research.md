# File Research: sources/virtualization/nbdkit/plugins/iso/Makefile.am

This Automake file builds the ISO-generating plugin when ISO tooling is available and the platform is not Windows.

Key behavior:
- Gated by `HAVE_ISO` and `!IS_WINDOWS`.
- Builds `nbdkit-iso-plugin.la` from `iso.c`.
- Includes nbdkit headers, common utilities, and current directory.
- Links common utils and optional Windows import library.
- Uses optional linker version script.
- Builds the man page when POD tooling is available.

Reason for Windows exclusion:
- Comment notes the plugin uses `open_memstream` to construct shell commands.
