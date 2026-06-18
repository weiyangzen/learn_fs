# File Research: sources/virtualization/nbdkit/plugins/info/Makefile.am

This Automake file builds the `info` plugin.

Key behavior:
- Builds `nbdkit-info-plugin.la` from `info.c`.
- Includes common headers and optional GnuTLS flags/libs for base64 support.
- Uses module/shared libtool flags and optional linker version script.
- Generates `nbdkit-info-plugin.1` with magic-parameter documentation insertion when POD tooling is available.

Integration:
- Base64 mode support depends on GnuTLS configuration macros and libraries.
