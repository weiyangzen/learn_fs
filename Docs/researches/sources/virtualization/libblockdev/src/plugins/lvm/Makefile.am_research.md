# File Research: sources/virtualization/libblockdev/src/plugins/lvm/Makefile.am

## Purpose

`Makefile.am` defines the Automake build rules for the libblockdev LVM plugin variants.

## Build Variants

The file conditionally builds two mutually related plugin libraries:

- `libbd_lvm.la` when `WITH_LVM` is enabled.
- `libbd_lvm-dbus.la` when `WITH_LVM_DBUS` is enabled.

Both variants install `lvm.h` under `$(includedir)/blockdev` when their corresponding build option is active.

## Shared Inputs

Both plugin variants share:

- `lvm.h`
- `lvm-private.h`
- `lvm-common.c`
- `vdo_stats.c`
- `vdo_stats.h`
- dependency checking helpers from `../check_deps.c`
- device-mapper logging helpers from `../dm_logging.c`

The non-D-Bus variant uses `lvm.c`; the D-Bus variant uses `lvm-dbus.c`.

## Compiler and Linker Settings

Both variants use GLib, GIO, devmapper, and YAML compiler/linker flags. The CLI-backed plugin additionally links JSON-GLib. Both libraries are built with:

- `-Wall -Wextra -Werror`
- `-version-info 3:0:0`
- `-Wl,--no-undefined`
- exported symbols matching `^bd_.*`
- include paths for generated headers, plugin-local headers, and shared plugin headers
- `PACKAGE_SYSCONF_DIR` defined from `$(sysconfdir)`

## Research Notes

This file is the switch point between two backend implementations for the same public LVM API: direct command/JSON handling in `lvm.c` and lvmdbusd/GDBus handling in `lvm-dbus.c`.
