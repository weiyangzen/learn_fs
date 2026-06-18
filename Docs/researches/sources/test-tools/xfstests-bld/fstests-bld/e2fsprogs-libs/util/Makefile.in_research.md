# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/Makefile.in

Purpose: `util/Makefile.in` builds utility programs used by the e2fsprogs-libs build, primarily the `subst` template substitution tool and generated `gen-tarball` script.

Important APIs, types, and functions: make targets include `all`, `subst`, `copy_sparse`, `gen-tarball`, `tarballs`, `clean`, `mostlyclean`, and `distclean`. Variables are Autoconf-substituted (`@srcdir@`, `@top_srcdir@`, `@INSTALL@`, `@MCONFIG@`) and build-tool variables include `BUILD_CC`, `BUILD_CFLAGS`, and `BUILD_LDFLAGS`.

Control flow: pattern rule compiles `.c` to `.o`; `subst` links `subst.o`; `gen-tarball` runs `config.status` with `CONFIG_FILES=util/gen-tarball` and makes the result executable; `tarballs` invokes the generated script for Debian, all, and subset tarballs. Clean targets remove binaries, objects, generated tarballs, and generated Makefile artifacts.

State and persistence: creates build outputs in the util build directory, especially `subst` and `gen-tarball`. `distclean` removes generated Makefile state.

Dependencies and integration points: relies on the top-level e2fsprogs build system, `MCONFIG`, `config.status`, and `subst.c`. `gen-tarball.in` is transformed into the executable script.

Risks: `copy_sparse` has a build target but is not included in `PROGS`, so it may not be built by default. The `clean` target removes `copy-sparse` while the target is `copy_sparse`, likely a stale hyphen/underscore mismatch. Build/host compiler distinction matters because `subst` runs during the build.

Test signals: run `make -C util all`, verify `subst` and executable `gen-tarball`, and run `make clean/distclean` in a disposable tree to catch stale artifact names.
