<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in

Source read: complete file, 237 lines, 6942 bytes, sha256 `f1fba893dd385596fa190f84765705f35d7555d539faf33fc86a9515ef90c307`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in_research.md`.

Purpose: autoconf-substituted make configuration template for the bundled e2fsprogs libraries. It centralizes installation paths, compiler/linker flags, tool variables, library names, warning flags, substitution tooling, ownership/mode defaults, and generic rules for config regeneration and dependency generation.

Important APIs/types/functions: defines make variables such as `prefix`, `root_prefix`, `bindir`, `libdir`, `CC`, `BUILD_CC`, `ALL_CFLAGS`, `ALL_LDFLAGS`, `LIBEXT2FS`, `LIBCOM_ERR`, `LIBBLKID`, static/profiled library variants, `INSTALL_*`, `MKINSTALLDIRS`, `SUBSTITUTE`, and `WFLAGS`. Rules include config.status regeneration, MCONFIG generation, `lib/substitute_sh`, `util/subst.conf`, Makefile regeneration, optional autoconf, `.depend`, `depend`, `gcc-wall`, and `gcc-wall-new`.

Control flow: included by generated makefiles through `@MCONFIG@`. Autoconf replaces `@...@` tokens and conditional `@ifGNUmake@`/`@ifNotGNUmake@` blocks. Dependency rules run the compiler with `-M`, transform paths with `sed`, wrap lines with Perl, and splice dependency output back into `Makefile.in` during `make depend`.

State and persistence behavior: generated build state includes `MCONFIG`, `util/subst.conf`, `lib/substitute_sh`, `.depend`, possibly updated `Makefile.in`, and rebuilt configure output. Install variables guide persistent installation of libraries, headers, and manuals elsewhere in the tree.

Dependencies and integration: integrates all e2fsprogs sub-makefiles with autoconf `config.status`, `configure.in`, `util/subst`, compiler dependency generation, and library build fragments in `lib/Makefile.*`. It is consumed by the top-level `Makefile.in` in this item and by subdirectories.

Risks: recursive make and autoconf substitutions make behavior highly environment-sensitive. `make depend` mutates source `Makefile.in`, which can dirty the tree. Warning flags force strict C99/GNU feature macros and may expose platform-specific issues. Incorrect library extension substitutions can break static/shared/profiled link paths.

Test signals: run configure to generate `MCONFIG`, then `make libs`, `make progs`, `make check`, and optionally `make gcc-wall`. Regeneration tests should verify `config.status` updates MCONFIG and Makefiles without unintended diffs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in -->
