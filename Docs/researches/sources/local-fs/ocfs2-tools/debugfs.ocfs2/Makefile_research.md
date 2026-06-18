# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/Makefile

## Role

This makefile builds and distributes the `debugfs.ocfs2` administrative debugger.

## Build Inputs

It compiles `main.c`, `commands.c`, `dump.c`, `utils.c`, `journal.c`, block/inode/path search helpers, lock dump helpers, system-directory stats, and network stats. It installs the binary under `$(root_sbindir)` and builds the `debugfs.ocfs2.8` man page.

## Libraries

It links against `libocfs2`, `libo2cb`, GLib, `com_err`, readline, AIO, and conditionally `libdlm_lt` and `libcmap` when configured.

## Distribution

The distribution list includes all source/header files, `README`, and the man-page template. It creates an `include` directory in distribution archives.
