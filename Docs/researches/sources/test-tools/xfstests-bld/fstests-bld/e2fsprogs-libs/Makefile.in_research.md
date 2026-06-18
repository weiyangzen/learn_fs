<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in

Source read: complete file, 144 lines, 4310 bytes, sha256 `82df8ace90c8c1d5732edf62b5047c741b0e18b13081bc472f90f3f3d9ca4cc6`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in_research.md`.

Purpose: top-level make template for building, installing, cleaning, and checking the bundled e2fsprogs library/program subset inside xfstests-bld.

Important APIs/types/functions: variables include `LIB_SUBDIRS`, `PROG_SUBDIRS`, `SUBDIRS`, generated type headers in `SUBS`, and feature-gated subdirectories for resize/debugfs/uuid/blkid. Targets include `all`, `subs`, `libs`, `progs`, `docs`, install/uninstall variants, recursive clean/distclean/depend/check targets, generated `ext2_types.h`, `blkid_types.h`, `uuid_types.h`, and local clean rules.

Control flow: `all` builds substitutions, libraries, programs, and docs. `subs` generates type headers and prerequisite tools like `compile_et` and `ext2_err.h` when their directories exist. Recursive targets iterate over configured subdirectories and invoke corresponding target names. Program recursion depends on library recursion. Install targets install programs, shared libs, docs, and, if program directories are absent, library-only artifacts.

State and persistence behavior: creates generated headers, build outputs across subdirectories, docs, spec files, and install artifacts. Clean targets remove generated type headers and local build/config files; distclean removes autoconf outputs and generated Makefiles; realclean can remove `configure`.

Dependencies and integration: includes `@MCONFIG@` from `MCONFIG.in`, depends on `config.status`, `util/subst`, `asm_types.h`, and subdirectory makefiles. This file is the recursive build coordinator for e2fsprogs-libs.

Risks: recursive targets skip missing directories silently, so misconfigured source subsets can produce partial builds without obvious failures. The `% : %.sh` suffix-style rule can influence script targets. Install logic has special library-only behavior when program directories are missing, which may surprise package rules.

Test signals: after configure, run `make all`, `make check`, `make install DESTDIR=...`, `make clean`, and `make distclean`. Verify generated type headers exist after `subs` and are removed by clean/distclean as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in -->
