# File Research: sources/local-fs/ocfs2-tools/Config.make.in

## Role

`Config.make.in` is the Autoconf-substituted make configuration template included by the project build system after `configure` generates `Config.make`.

## Build Variables

It exports package/version fields, install prefixes, root install prefixes, Python execution directory, toolchain commands, install commands, warning flags, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, vendor identity, and library flags for `com_err`, `uuid`, `aio`, `readline`, `glib`, `blkid`, and Python.

## Feature Gates

It carries configure decisions into makefiles, including `HAVE_BLKID`, `LIBDLM_FOUND`, `BUILD_OCFS2CONSOLE`, `BUILD_DEBUGOCFS2`, Corosync/controld support, Pacemaker/CMAN/CMAP/FSDLM support, debug mode, debug executables, and dynamic/static build mode for fsck and control tools.

## Notable Constraints

The template appends common warnings to caller-provided `CFLAGS`. Downstream makefiles depend on these substitutions being present, so configure failures or stale generated `Config.make` can change which OCFS2 tools are built.
