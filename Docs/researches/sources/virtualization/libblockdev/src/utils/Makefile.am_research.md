# File Research: sources/virtualization/libblockdev/src/utils/Makefile.am

This Automake file builds and installs the shared libblockdev utility library.

Build targets:
- Builds `libbd_utils.la`.
- Uses GLib, udev, and kmod CFLAGS.
- Enforces `-Wall -Wextra -Werror`.
- Uses libtool version info `3:0:0` and linker `--no-undefined`.
- Links GLib, math, GIO, udev, and kmod libraries.

Sources:
- `utils.h`
- `exec.c/.h`
- `sizes.h`
- `extra_arg.c/.h`
- `dev_utils.c/.h`
- `module.c/.h`
- `dbus.c/.h`
- `logging.c/.h`

Install outputs:
- Public headers under `$(includedir)/blockdev`.
- `blockdev-utils.pc` under pkg-config directory.

Research relevance:
- The files in this group are part of a shared utility library used by plugins, not private plugin-only helpers.
