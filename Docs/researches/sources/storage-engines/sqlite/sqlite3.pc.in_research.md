# sources/storage-engines/sqlite/sqlite3.pc.in

## Purpose

`sqlite3.pc.in` is the primary pkg-config template for SQLite 3. It tells downstream build systems how to compile against installed SQLite headers and link against `libsqlite3`.

## Important Fields and Substitutions

The template defines standard installation variables `prefix`, `exec_prefix`, `libdir`, and `includedir`. Public metadata is `Name: SQLite`, `Description: SQL database engine`, and `Version: @PACKAGE_VERSION@`. The dynamic link line is `Libs: -L${libdir} -lsqlite3`. Static/private dependencies are expanded into `Libs.private` from `@LDFLAGS_MATH@`, `@LDFLAGS_ZLIB@`, `@LDFLAGS_DLOPEN@`, `@LDFLAGS_PTHREAD@`, and `@LDFLAGS_ICU@`. Header discovery is `Cflags: -I${includedir}`.

## Control Flow and Generation

The template is processed by SQLite's configure/build system into `sqlite3.pc`, which `main.mk` can install through `install-pc`. It contains no executable logic, but its substitutions must reflect the configured library feature set and install prefix.

## State and Persistence Behavior

The generated `sqlite3.pc` persists the configured version, install directories, public link flag, and private static-link dependencies. Consumers invoking `pkg-config sqlite3 --libs` get only the public `-L`/`-lsqlite3` flags, while `pkg-config sqlite3 --static --libs` also receives the `Libs.private` dependencies.

## Dependencies and Integration Points

This file integrates with `pkg-config`, `main.mk` install paths, configure-detected feature libraries, and downstream C/C++ build systems. Its private dependency list mirrors feature-specific linker buckets in the makefile, including math, zlib, dlopen, pthread, and ICU. Correctness depends on the generated file matching how `libsqlite3` was actually linked and installed.

## Risks and Test Signals

Risks are mostly packaging-related: missing private libraries break static linking, stale `@PACKAGE_VERSION@` misleads dependency checks, and incorrect `libdir`/`includedir` causes consumers to use a different SQLite than intended. ICU and zlib settings are especially sensitive because they may be optional at configure time. Test signals are successful `pkg-config --modversion sqlite3`, correct `pkg-config --cflags --libs sqlite3` output, successful dynamic consumer link, and successful static consumer link when static packages are expected.
