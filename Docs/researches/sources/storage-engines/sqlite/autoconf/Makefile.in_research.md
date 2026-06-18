<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/Makefile.in -->
# sources/storage-engines/sqlite/autoconf/Makefile.in

## Purpose
This is the trimmed Makefile template for SQLite's autoconf/amalgamation bundle. Unlike the canonical template, it contains direct rules for building and installing the amalgamated `sqlite3` shell, shared library, static library, headers, pkg-config file, man page, and distribution archive.

## Important APIs, Types, And Functions
Important make variables include `TOP`, `PACKAGE_VERSION`, `B.*`/`T.*` filename extensions, install directories, `INSTALL`, `AR`, `CC`, `ENABLE_LIB_SHARED`, `ENABLE_LIB_STATIC`, `HAVE_WASI_SDK`, `CFLAGS`, `LDFLAGS.*`, `OPT_FEATURE_FLAGS`, `libsqlite3.*`, `ENABLE_STATIC_SHELL`, and `STATIC_CLI_SHELL`. Key targets include `sqlite3.o`, `$(libsqlite3.DLL)`, `$(libsqlite3.LIB)`, `sqlite3$(T.exe)`, `install-dll-*`, `install-lib`, `install-shell`, `install-headers`, `install-pc`, `install-man1`, `clean`, `distclean`, and `dist`.

## Control Flow
Configure substitutes platform and feature values into this template. `sqlite3.o` compiles `$(TOP)/sqlite3.c`. Shared-library and static-library targets are gated into `all` via suffix targets keyed by `ENABLE_LIB_SHARED` and `ENABLE_LIB_STATIC`. The shell link path switches between directly linking `sqlite3.c` and linking against the produced shared library using `ENABLE_STATIC_SHELL`; fully static shell flags are controlled by `STATIC_CLI_SHELL`. Install targets create destination directories, install artifacts, and platform-specific DLL rules create Unix, Darwin, MSYS, MinGW, or Cygwin layouts. `dist` copies `DIST_FILES` into `sqlite-$(PACKAGE_VERSION)` and creates a `.tar.gz`.

## State And Persistence Behavior
Build artifacts include `sqlite3.o`, `libsqlite3$(T.dll)` variants, `libsqlite3$(T.lib)`, optional import libraries, `sqlite3$(T.exe)`, `sqlite3.pc`, `sqlite_cfg.h`, `Makefile`, `config.*`, and `jimsh0$(T.exe)`. Install rules write into `$(DESTDIR)`-prefixed bin/lib/include/pkgconfig/man directories and may replace or create shared-library symlinks such as `.0`, `.$(PACKAGE_VERSION)`, and optional legacy `.0.8.6` links.

## Dependencies And Integration Points
The file integrates the autoconf bundle with autosetup reconfiguration (`AS_AUTORECONFIG`), SQLite amalgamation files (`sqlite3.c`, `sqlite3.h`, `sqlite3ext.h`, `shell.c`), pkg-config, man-page installation, platform linkers, and OS-specific shared-library naming. It carries compatibility behavior for libtool-era SQLite shared-object names and Windows-style import libraries.

## Risks
Shared-library install rules are platform-sensitive and can delete/relink legacy symlinks. Link flag ordering is explicitly important on some platforms. The shell gating through `HAVE_WASI_SDK` is non-obvious: the target suffix rules decide whether the shell is built/installed. The bundle is trimmed from canonical `main.mk`, so changes must stay synchronized with canonical install and link behavior.

## Test Signals
Primary signals are successful configure, `make all` under shared/static combinations, correct `sqlite3` shell linkage, `make install DESTDIR=...` producing the expected platform layout, `pkg-config` file installation, clean/distclean removal of generated artifacts, and `make dist` producing `sqlite-$(PACKAGE_VERSION).tar.gz`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/Makefile.in -->
