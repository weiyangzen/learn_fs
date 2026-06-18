# File Research: sources/local-fs/ntfs-3g/src/Makefile.am

## Purpose

Automake build definition for the NTFS-3G FUSE driver programs and probe helper in `src/`.

## Build Products

When `ENABLE_NTFS_3G` is true:

- Installs `ntfs-3g.probe` as a normal binary.
- Installs `ntfs-3g` and `lowntfs-3g` as root binaries.
- Installs man pages:
  - `ntfs-3g.8`
  - `ntfs-3g.probe.8`

## FUSE Selection

- If `FUSE_INTERNAL` is enabled:
  - `FUSE_CFLAGS = -I$(top_srcdir)/include/fuse-lite`
  - `FUSE_LIBS = $(top_builddir)/libfuse-lite/libfuse-lite.la`
- Otherwise:
  - Uses `$(FUSE_MODULE_CFLAGS)` and `$(FUSE_MODULE_LIBS)` from external FUSE detection.

## Plugin Configuration

When plugins are not disabled:

- Defines plugin installation directory as `$(libdir)/ntfs-3g`.
- Adds `-DPLUGIN_DIR="$(plugindir)"` via `PLUGIN_CFLAGS`.
- Install hook creates the plugin directory.

## Program Definitions

- `ntfs-3g`
  - Sources: `ntfs-3g.c`, `ntfs-3g_common.c`
  - CFLAGS include `-DFUSE_USE_VERSION=26`, FUSE flags, libntfs-3g includes, plugin flags.
  - Links with `$(LIBDL)`, FUSE, and `libntfs-3g.la`.
- `lowntfs-3g`
  - Sources: `lowntfs-3g.c`, `ntfs-3g_common.c`
  - Uses the same CFLAGS and LDADD pattern as `ntfs-3g`.
- `ntfs-3g.probe`
  - Source: `ntfs-3g.probe.c`
  - Links only against `libntfs-3g.la`.

## Static Build Handling

If `REALLYSTATIC` is enabled, each program uses `$(AM_LDFLAGS) -all-static`.

## Install Hooks

- Runs `ldconfig` when `RUN_LDCONFIG` is true.
- If `ENABLE_MOUNT_HELPER` is true:
  - Creates `/sbin/mount.ntfs-3g` symlink to rootbin `ntfs-3g`.
  - Creates `/sbin/mount.lowntfs-3g` symlink to rootbin `lowntfs-3g`.
  - Creates manpage symlinks for both mount helpers.
  - Removes those symlinks on uninstall.

## Role in Source Tree

This file wires the high-level and low-level NTFS-3G FUSE drivers into the autotools build, controlling whether they use bundled or external FUSE, whether reparse plugins are supported, and whether mount-helper compatibility symlinks are installed.
