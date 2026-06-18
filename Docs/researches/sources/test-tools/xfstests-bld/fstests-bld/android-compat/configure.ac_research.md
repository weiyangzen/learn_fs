# sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure.ac

Purpose: concise Autoconf source for the android-compat build system.

Important APIs and functions: uses `AC_PREREQ(2.59)`, `AC_INIT(lio_listio.c)`, `AC_CONFIG_AUX_DIR(../e2fsprogs-libs/config)`, `AC_CANONICAL_BUILD`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, `AC_PROG_RANLIB`, and `AC_OUTPUT(Makefile)`.

Control flow: Autoconf expands this into `configure`, which validates source identity, canonicalizes build/host, locates compiler and ranlib, and substitutes `Makefile.in`.

State and persistence: source-level build metadata only; generated outputs are `configure` and, at configure time, `Makefile`.

Dependencies and integration: depends on Autoconf and e2fsprogs config auxiliary scripts. It feeds `autoconf` when regenerating the script.

Risks: minimal checks mean missing headers/functions are not detected here; the compatibility library assumes its source code is suitable for the target.

Test signals: `autoconf` can regenerate `configure`, and `./configure` can create `Makefile`.
