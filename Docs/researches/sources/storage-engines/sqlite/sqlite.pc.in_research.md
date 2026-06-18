# sources/storage-engines/sqlite/sqlite.pc.in

## Purpose

`sqlite.pc.in` is a pkg-config template for a library named `sqlite`. It describes include and linker flags for consumers that expect the legacy or alternate `-lsqlite` library name rather than SQLite 3's normal `-lsqlite3`.

## Important Fields and Substitutions

The template defines `prefix`, `exec_prefix`, `libdir`, and `includedir` using configure substitution variables. It publishes `Name: SQLite`, `Description: SQL database engine`, `Version: @RELEASE@`, `Libs: -L${libdir} -lsqlite`, `Libs.private: @LIBS@`, and `Cflags: -I${includedir}`.

## Control Flow and Generation

There is no runtime control flow. A configure or packaging step substitutes `@prefix@`, `@exec_prefix@`, `@libdir@`, `@includedir@`, `@RELEASE@`, and `@LIBS@` to produce an installable `.pc` file. pkg-config consumers then use the generated metadata to compile and link client programs.

## State and Persistence Behavior

The generated file is installed under a pkg-config directory, typically `${libdir}/pkgconfig`. It persists build-time installation paths and private linker dependencies. `Libs.private` is only used by pkg-config for static linking, so it can affect whether static consumers pull in math, pthread, zlib, dlopen, or other platform libraries.

## Dependencies and Integration Points

The template integrates with autotools-style substitution variables and downstream `pkg-config` tooling. It is separate from the `main.mk` `install-pc` target, which installs `sqlite3.pc`; this template may be used by another compatibility packaging path. The important downstream integration point is the library name: it advertises `-lsqlite`, so it is only correct for builds that actually produce or package that library name.

## Risks and Test Signals

The main risk is divergence from the SQLite 3 pkg-config file. `@RELEASE@` and `@LIBS@` differ from the newer `sqlite3.pc.in` variables, and the library flag is `-lsqlite`, not `-lsqlite3`. If a package installs this file without a matching library, pkg-config checks may pass compilation flags but fail at link time. Test signals are successful substitution, `pkg-config --cflags --libs` output pointing at the intended prefix, and a small consumer program linking successfully with both dynamic and static pkg-config modes.
