# File Research: sources/local-fs/gfs2-utils/configure.ac

## Purpose
Autoconf configuration for `gfs2-utils`, defining package identity, compiler/tool checks, dependency discovery, feature flags, generated files, and the final configure summary.

## Main Elements
- Package setup: requires Autoconf 2.69, initializes `gfs2-utils` version `3.6.1.1.dev`, Automake, libtool, gettext, config headers, and macro directory.
- Prefix sanitation: defaults prefix/sysconf/localstate/libdir to `/usr`, `/etc`, `/var`, and `/usr/lib` or `/usr/lib64`.
- Tool checks: requires GNU make, C compiler with C99, flex, bison, install/ln/make helpers.
- Helper shell functions: `cc_supports_flag()` and `check_lib_no_libs()`.
- Feature options: `--enable-debug`, `--enable-gcov`, `--enable-gprof`, `--with-udevdir`, `--with-testvol`.
- Dependencies: Check unit test framework, zlib, blkid, uuid, bzip2, ncurses, libintl/gettext.
- Compiler flags: large-file defines, include paths, debug/optimization/fortify, optional coverage/profiling, and probed warning flags.
- Outputs: all Makefiles under `gfs2`, `doc`, `tests`, and `po`, plus `tests/atlocal` and spec file.

## Dependencies And Integration
Feeds generated `make/clusterautoconfig.h` and all recursive Automake files. `AM_CONDITIONAL([HAVE_CHECK])` controls inclusion of unit-test make fragments.

## Risk Notes
The script calls `LT_INIT` twice. Several fallback library checks intentionally mutate and restore `LIBS`; mistakes there would over-link targets. `local` in shell helper functions assumes a shell supporting it during configure execution.
