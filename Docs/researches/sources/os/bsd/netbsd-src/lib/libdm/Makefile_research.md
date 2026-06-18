# File Research: sources/os/bsd/netbsd-src/lib/libdm/Makefile

This NetBSD makefile builds the `libdm` device-mapper userland library.

Key build settings:
- `LIB= dm`
- `SRCS= libdm_ioctl.c`
- Installs `dm.h` to `/usr/include`.
- Installs manual page `dm.3`.
- Links against `libprop` through `LIBDPLIBS`.
- Sets `USE_SHLIBDIR=yes` and disables fortification by default with `USE_FORT?= no`.

Conditional behavior:
- If `RUMP_ACTION` is defined, adds `-DRUMP_ACTION` to `CPPFLAGS`, enabling rump syscall paths in `libdm_ioctl.c`.

Integration:
- This build file connects the proplib-backed ioctl wrapper to NetBSD's device-mapper driver interface.
