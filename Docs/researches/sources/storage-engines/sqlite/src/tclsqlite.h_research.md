# Research: sources/storage-engines/sqlite/src/tclsqlite.h

## Purpose

`tclsqlite.h` is the small interface shim that SQLite components use instead
of including `tcl.h` directly. It centralizes platform-specific Tcl include
selection, calling-convention decoration, and Tcl 8.6/9.0 compatibility types
for SQLite's Tcl extension and Tcl-based test components.

The header explicitly warns that edits must be mirrored in `tclsqlite.c`,
because that C file carries an embedded copy for amalgamated builds.

## Important Macros And Behavior

- If `INCLUDE_SQLITE_TCL_H` is defined, the header includes `sqlite_tcl.h`.
  This supports Windows STDCALL builds where the MSVC makefile creates a
  customized Tcl header with SQLite's needed calling conventions.
- Otherwise it includes the system `<tcl.h>` and defines `SQLITE_TCLAPI` to an
  empty macro if Tcl did not provide one.
- For Tcl 9, it defines `CONST` as `const`.
- For older Tcl headers that do not define `Tcl_Size`, it aliases
  `Tcl_Size` to `int`.

## Control Flow And State

The file has only preprocessor control flow and no runtime state. Its role is
to make downstream C code compile with consistent type names and function
declarations across Tcl header variants. The repeated mirror-warning comments
are part of the maintenance contract.

## Dependencies And Integration Points

The direct dependency is either `sqlite_tcl.h` or `<tcl.h>`. The consumers are
SQLite's Tcl extension (`tclsqlite.c`), Tcl-enabled test files, and any
subcomponent that needs Tcl APIs while respecting SQLite's build conventions.

Because `tclsqlite.c` embeds a copy, this header is not the only source of
truth at build time. Changes must be synchronized manually or separate-source
and amalgamated builds may diverge.

## Risks

The main risk is drift between this header and the copy inside `tclsqlite.c`.
A missing `SQLITE_TCLAPI`, `Tcl_Size`, or `CONST` compatibility change can
break one build mode while the other continues to compile. Windows STDCALL
builds are also sensitive to choosing the correct customized Tcl header.

The compatibility definitions are intentionally minimal. Adding broader Tcl
compatibility here should be checked against Tcl's own headers to avoid
conflicting typedefs or macro definitions.

## Test Signals

Validation should include separate-source and amalgamated Tcl extension builds,
Windows builds with `INCLUDE_SQLITE_TCL_H`, normal Unix-like builds with
system `<tcl.h>`, Tcl 8.6 builds where `Tcl_Size` may need compatibility, and
Tcl 9 builds where `CONST` behavior and `SQLITE_TCLAPI` declarations remain
accepted.
