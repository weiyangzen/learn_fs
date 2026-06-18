# File Research: sources/local-fs/udftools/configure.ac

Autoconf input for udftools version `2.3`.

Configuration responsibilities:
- Requires Autoconf 2.64.
- Initializes package metadata and `include/config.h`.
- Enables Automake and Libtool.
- Requires a C99-capable compiler.
- Disables shared libraries.
- Checks for `ln -s` and `mkdir -p`.
- Detects readline through pkg-config first, falling back to `AC_CHECK_LIB` and header checks.
- Checks inline support, endian layout, and large-file support.
- Detects udev via pkg-config and exposes `UDEVDIR`.
- Defines Automake conditionals for readline and udev support.

Generated Makefiles:
- Root
- `libudffs`
- `mkudffs`
- `cdrwtool`
- `pktsetup`
- `udffsck`
- `udfinfo`
- `udflabel`
- `wrudf`
- `doc`

Key role: central portability/build feature detection for all tools.
