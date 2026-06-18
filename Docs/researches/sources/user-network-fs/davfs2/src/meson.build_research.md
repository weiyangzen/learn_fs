<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/meson.build -->
# Research: sources/user-network-fs/davfs2/src/meson.build

Purpose: builds and installs the two davfs2 executables: `mount.davfs` and `umount.davfs`.

Important APIs: `mount_davfs_sources` includes `mount_davfs.c`, `dav_fuse.c`, `cache.c`, `webdav.c`, and `kernel_interface.c`; `umount_davfs_sources` includes `umount_davfs.c`. Two `executable()` calls use `config_inc`, dependencies `[neon_dep, intl_dep]`, `install: true`, and `install_dir: davfs2_sbindir`.

Control flow and integration: root `meson.build` enters this directory after configuring `config.h` and dependencies. `mount.davfs` links the full runtime stack; `umount.davfs` is standalone but still receives the same include dir and dependencies.

State and persistence: build artifact definitions only. Installed binaries are placed under configured sbindir.

Dependencies: parent variables `config_inc`, `neon_dep`, `intl_dep`, and `davfs2_sbindir`; source files must match NLS `POTFILES.in`.

Risks: linking `umount.davfs` against `neon_dep` is likely unnecessary but harmless; if neon is unavailable the whole project fails because mount helper needs it. Source-list drift can break translation extraction or miss new runtime modules.

Test signals: Meson compile/install, ldd/link dependency inspection, executable smoke tests for `--help`/`--version`, and package file-list checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/meson.build -->
