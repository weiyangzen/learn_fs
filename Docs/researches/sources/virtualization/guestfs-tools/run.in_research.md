# File Research: sources/virtualization/guestfs-tools/run.in

Autoconf-substituted shell wrapper for running uninstalled libguestfs tools from the build tree.

Key behavior:
- Optional `--test` mode wraps commands in a timeout and prints standardized failure/timeout messages.
- Computes absolute source/build directories from `@abs_srcdir@` and `@abs_builddir@`.
- Sets `LIBGUESTFS_TMPDIR` and `LIBGUESTFS_CACHEDIR` to build-tree `tmp`, creates it, and tries to copy `/tmp` SELinux context.
- Prepends build subdirectories for many virt tools to `PATH`.
- Defaults `VIRT_BUILDER_DIRS` to the local builder test website when unset.
- Enables glibc malloc debugging/perturbation unless running under `VG`.
- Uses `libtool --mode=execute` if libtool is available.
- Clears GNOME keyring environment variables.
- In test mode, uses up to a 4-hour timeout with 30-second kill grace where supported.

Research notes:
- This script is central to tests in this group; `TESTS_ENVIRONMENT` commonly invokes `$(top_builddir)/run --test`.
