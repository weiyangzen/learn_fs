# File Research: sources/virtualization/libblockdev/src/plugins/smart/Makefile.am

## Purpose

Automake build definition for the SMART plugin variants.

## Main Responsibilities

- Install `smart.h` when either SMART backend is enabled.
- Build `libbd_smart.la` when `WITH_SMART` is enabled.
- Build `libbd_smartmontools.la` when `WITH_SMARTMONTOOLS` is enabled.
- Share common SMART sources and dependency-check sources between variants.

## Build Behavior

For `WITH_SMART`:
- Builds `libbd_smart.la`.
- Uses `GLIB_CFLAGS`, `GIO_CFLAGS`, `SMART_CFLAGS`, and `DRIVEDB_H_CFLAGS`.
- Links blockdev utils, GLib/GIO, and SMART backend libraries.
- Sources include:
  - `smart.h`
  - `smart-private.h`
  - `smart-common.c`
  - `drivedb-parser.c`
  - `libatasmart.c`
  - `../check_deps.c`
  - `../check_deps.h`

For `WITH_SMARTMONTOOLS`:
- Builds `libbd_smartmontools.la`.
- Adds `JSON_GLIB_CFLAGS` and links `JSON_GLIB_LIBS`.
- Sources include:
  - `smart.h`
  - `smart-private.h`
  - `smart-common.c`
  - `drivedb-parser.c`
  - `smartmontools.c`
  - `../check_deps.c`
  - `../check_deps.h`

## Notable Details

- Both libraries use `-version-info 3:0:0`, `--no-undefined`, and export symbols matching `^bd_.*`.
- Both define `PACKAGE_SYSCONF_DIR` for runtime config path handling.
- `drivedb-parser.c` is common to both SMART implementations.
