# File Research: sources/virtualization/libblockdev/src/plugins/nvme/Makefile.am

## Role
Automake build definition for the NVMe plugin shared library.

## Build Targets
- Builds `libbd_nvme.la` as a libtool library.
- Installs `nvme.h` under the blockdev include directory.

## Compiler and Linker Inputs
- CFLAGS include GLib, GIO, NVMe package flags, `-Wall`, `-Wextra`, and `-Werror`.
- LIBADD links the local blockdev utils library plus GLib, GIO, and NVMe libraries.
- LDFLAGS set the utils library path, libtool version info `3:0:0`, no undefined symbols, and exported symbols matching `^bd_.*`.
- CPPFLAGS include generated include paths, plugin include paths, the current directory, and `PACKAGE_SYSCONF_DIR`.

## Sources
Includes NVMe public/private headers and implementation files for core logic, info, errors, operations, fabrics, and shared dependency checking.
