# sources/storage-engines/sqlite/main.mk

## Purpose

`main.mk` is SQLite's central POSIX-compatible makefile include. It is not a standalone configured makefile; it expects an outer makefile or configure-generated wrapper to provide host/target compiler variables, package version, Tcl settings, feature flags, installation prefixes, platform suffixes, and optional linkage choices. Its job is to build the generated SQLite artifacts (`sqlite3.c`, `sqlite3.h`, `shell.c`, parser/opcode tables, FTS5 amalgamation), static and shared libraries, the CLI shell, Tcl extension, test fixture, fuzzers, developer tools, release archives, install targets, and cleanup targets.

## Important APIs, Targets, and Variables

The file exposes configuration variables rather than C APIs. Important build inputs include `TOP`, `PACKAGE_VERSION`, `B.cc`, `T.cc`, `AR`, `B.exe`, `T.exe`, `T.dll`, `T.lib`, `HAVE_TCL`, `TCLSH_CMD`, `TCL_CONFIG_SH`, `ENABLE_LIB_SHARED`, `ENABLE_LIB_STATIC`, `USE_AMALGAMATION`, `LINK_TOOLS_DYNAMICALLY`, `AMALGAMATION_GEN_FLAGS`, `OPT_FEATURE_FLAGS`, `OPTS`, `SHELL_OPT`, and feature-scoped flag buckets such as `LDFLAGS.pthread`, `LDFLAGS.zlib`, `LDFLAGS.readline`, and `CFLAGS.icu`. The makefile deliberately separates common compiler flags, SQLite-library flags, extension flags, Tcl flags, and feature libraries so that different deliverables do not inherit inappropriate options.

Core targets include `all`, `lib`, `so`, `sqlite3.c`, `sqlite3.h`, `.target_source`, `sqlite3.o`, `$(libsqlite3.LIB)`, `$(libsqlite3.DLL)`, `sqlite3$(T.exe)`, `sqlite3d$(T.exe)`, `testfixture$(T.exe)`, `fuzzcheck$(T.exe)`, `sessionfuzz$(T.exe)`, `mptester$(T.exe)`, `sqlite3_analyzer$(T.exe)`, `sqldiff$(T.exe)`, `dbhash$(T.exe)`, `sqlite3_rsync$(T.exe)`, `tclsqlite3$(T.exe)`, `$(libtclsqlite3.DLL)`, `install`, `install-dll-*`, `install-lib`, `install-headers`, `install-pc`, `install-man1`, `devtest`, `releasetest`, `mptest`, `tidy`, `clean`, `distclean`, and `show-variables`.

## Control Flow and Build Graph

The file starts with defaulted variables and sanity checks, then defines source inventories (`LIBOBJS0`, `LIBOBJS1`, `SRC`, `TESTSRC`, `TESTSRC2`, extension headers, test programs, fuzz data). `LIBOBJ` switches between the full object list and the amalgamation object using `USE_AMALGAMATION`. `MAKE_SANITY_CHECK` validates essential variables and the top source directory before object builds.

Generated-code flow is: build `jimsh` or use `B.tclsh`, generate `sqlite3.h` with `mksqlite3h.tcl`, copy sources into `tsrc`, compress VDBE code, generate parser/opcode/pragma/keyword files using Lemon and Tcl/C tools, then run `mksqlite3c.tcl` to produce the amalgamation. FTS5 has its own Lemon grammar and `mkfts5c.tcl` amalgamation flow. The shell is assembled by `mkshellc.tcl` from `shell.c.in` and extension sources. Test fixture and tools either compile `sqlite3.c` directly or link against `libsqlite3` depending on target semantics and `LINK_TOOLS_DYNAMICALLY`.

The install graph is additive: `install` depends on enabled shared-library, static-library, header, Tcl, shell, manpage, and pkg-config install targets. Shared-library installation has platform-specific rules for Unix generic, Darwin, MSYS, MinGW, and Cygwin, including compatibility symlinks for historical `libsqlite3.so.0` and optional `libsqlite3.so.0.8.6`.

## State and Persistence Behavior

The makefile produces persistent build outputs in the build directory: generated C/header files, object files, static and shared libraries, test binaries, tool binaries, Tcl package files, zip/tar archives, and temporary source directories such as `tsrc`. It installs files under `DESTDIR` plus `bindir`, `libdir`, `includedir`, `mandir`, and `libdir/pkgconfig`. It also writes helper files such as `.main.mk.checks`, `.target_source`, `has_tclsh84`, `has_tclsh85`, `pkgIndex.tcl`, `.tclenv.sh`, and generated resource headers.

Cleanup state is separated by target. `tidy` removes build products but preserves configure outputs and test logs; `clean` additionally removes test directories/log artifacts; `distclean` delegates full cleanup expectations to `Makefile.in` while depending on `clean`. This split is important for out-of-tree builds and package builds that should not discard configure results unnecessarily.

## Dependencies and Integration Points

The file integrates with SQLite's source tree (`src`, `ext`, `tool`, `test`, `autosetup`) and with configure/autosetup wrappers. It depends on a POSIX shell, install-compatible `install`, C compiler(s), `ar`, Tcl or JimTcl for code generation, Lemon for parser generation, optional readline/linenoise, zlib, pthread, dlopen, math, ICU, Valgrind for selected tests, `nm`, `egrep`, `sed`, `strip`, and platform linkers. It also integrates with generated `sqlite3.pc` for pkg-config, Tcl's `tclConfig.sh`, source verification tools, release packaging scripts, and SQLite's `testrunner.tcl`.

Cross-build integration is explicit: `B.cc` builds host tools such as Lemon, `mkkeywordhash`, `mksourceid`, `src-verify`, and JimTcl, while `T.cc` builds target deliverables. `HAVE_WASI_SDK` disables shell build/install paths that do not apply to WASI. `LINK_TOOLS_DYNAMICALLY` changes whether tools embed or dynamically link SQLite.

## Risks and Edge Cases

The largest risk is portability. The file is intentionally POSIX make compatible and warns against GNU make-isms, so adding GNU-only syntax can break BSD make or downstream package builds. A second risk is flag scoping: applying `CFLAGS`, `LDFLAGS`, Tcl, readline, ICU, or sanitizer flags too broadly can break shared-library PIC requirements, cross-compilation, or tool linkage. Generated parser-related flags must be present when Lemon and keyword generation run, not just when compiling the final amalgamation.

Install risks include platform-specific shared-library naming, stale `libsqlite3.la`, historical symlink compatibility, unquoted spaces in install paths, and import-library handling on Unix-like Windows environments. Test and release targets have duplicated behavior in Tcl runner scripts, so updating make recipes without updating scheduler metadata can desynchronize CI behavior. `mptester`, fuzzers, and testfixture targets rely on static/internal SQLite symbols and specific compile-time options; changing `USE_AMALGAMATION` or symbol visibility can break them.

## Test Signals

Primary build signals are successful `all`, `lib`, `so`, `sqlite3$(T.exe)`, generated amalgamation, and install target completion. Source integrity signals include `srctree-check`, `sourcetest`, `verify-source`, and `checksymbols`. Runtime and regression signals include `devtest`, `mdevtest`, `sdevtest`, `releasetest`, `tcltest`, `testrunner`, `smoketest`, `fuzztest`, `valgrindfuzz`, `mptest`, and `threadtest`. Packaging signals are successful `amalgamation-tarball`, `snapshot-tarball`, `sqlite-src.zip`, `sqlite-amalgamation.zip`, `tool-zip`, and `snapshot-zip`.
