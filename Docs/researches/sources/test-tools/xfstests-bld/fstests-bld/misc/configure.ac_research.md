# sources/test-tools/xfstests-bld/fstests-bld/misc/configure.ac

Purpose: source Autoconf input for generating `misc/configure`.

Important APIs, types, and functions: uses `AC_PREREQ(2.59)`, `AC_INIT(fname_benchmark.c)`, `AC_CONFIG_AUX_DIR(../e2fsprogs-libs/config)`, `AC_CANONICAL_BUILD`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, and `AC_OUTPUT(Makefile)`.

Control flow: when processed by Autoconf, it creates a configure script that validates source presence, locates auxiliary scripts, canonicalizes build/host, finds a C compiler, and generates `Makefile`.

State and persistence: no runtime state itself; regenerating from it updates the generated `configure` script.

Dependencies and integration points: tied to `misc/Makefile.in`, `misc/configure`, and the e2fsprogs-libs config auxiliary directory.

Risks: minimal and intentionally simple. Any new misc utility requiring library/header checks must add tests here and regenerate `configure`.

Test signals: run `autoconf` and compare/regenerate `configure`, then run generated configure and make.
