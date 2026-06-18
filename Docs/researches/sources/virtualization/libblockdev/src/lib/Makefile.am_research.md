# File Research: sources/virtualization/libblockdev/src/lib/Makefile.am

## Role
Build rules for the central `libblockdev.la` library, its generated plugin API wrappers, GObject introspection metadata, installed headers, and pkg-config file.

## Build Targets
- Includes `$(INTROSPECTION_MAKEFILE)` and descends into `plugin_apis`, where `.api` files generate C/H boilerplate wrappers.
- Builds `libblockdev.la` from `blockdev.c`, `blockdev.h`, `plugins.c`, and `plugins.h`.
- Links `libblockdev.la` with `../utils/libbd_utils.la`, GLib/GObject, and `-ldl`.
- Uses `-version-info 3:0:0`, `--no-undefined`, and exports symbols matching `^bd_.*`.
- Installs `blockdev.h` and `plugins.h` under `$(includedir)/blockdev`.
- Installs `${builddir}/blockdev.pc` into `$(libdir)/pkgconfig`.

## Introspection
- If `HAVE_INTROSPECTION` is enabled, it gathers generated plugin API headers for mdraid, swap, btrfs, lvm, crypto, dm, loop, mpath, part, fs, nvdimm, nvme, smart, and conditionally s390.
- Adds utility sources and core library sources to the GIR input set.
- Produces `BlockDev-3.0.gir` and corresponding typelib with `--identifier-prefix=BD` and `--symbol-prefix=bd`.

## Dependencies and Interactions
- The generated `blockdev.c` is derived from `blockdev.c.in`; this Makefile treats `blockdev.c` as maintainer-clean.
- The generated plugin API C files are included directly by `blockdev.c.in`, so `plugin_apis` generation is a prerequisite for a complete build.
- Conditional GObject flags for Btrfs and LVM reflect plugin API exposure that needs GObject type data.

## Filesystem/Storage Relevance
This is the build nexus for libblockdev's runtime plugin-loader API. It exposes a unified library interface while plugin implementations remain separate shared libraries.
