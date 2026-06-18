<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/pkgIndex.tcl.in -->
# sources/storage-engines/sqlite/autoconf/tea/pkgIndex.tcl.in

## Purpose
This is the Tcl package index template generated for teaish-built extensions. It registers `package ifneeded` scripts that load the correct Tcl 8 or Tcl 9 extension library and optionally source package initialization code.

## Important APIs, Types, And Functions
The template uses Tcl package APIs: `package vsatisfies`, `package provide Tcl`, and `package ifneeded`. Generated values include `TEAISH_PKGNAME`, `TEAISH_VERSION`, `TEAISH_DLL9`, `TEAISH_DLL8`, `TEAISH_LOAD_PREFIX`, `TEAISH_PKGINIT_TCL_TAIL`, `TEAISH_ENABLE_DLL`, and optional `TEAISH_VSATISFIES_CODE`. Runtime code uses `apply`, `file join`, `file extension`, `string tolower`, `load`, `file exists`, and `source -encoding utf-8`.

## Control Flow
The index first runs optional version-satisfaction code, then branches on whether the running Tcl version satisfies `9.0-`. The Tcl 9 branch loads the Tcl 9 DLL name when DLL support is enabled and sources optional init script. The Tcl 8 branch loads the Tcl 8 DLL when its extension looks like a native shared library; otherwise it calls `load {}` with the load prefix, supporting statically linked or non-library cases. Both branches register deferred code with `package ifneeded` rather than loading immediately.

## State And Persistence Behavior
This file is installed as package metadata under `TCLLIBDIR`. Runtime state is Tcl's package registry entry and, when requested, the loaded native extension and sourced init script. It does not mutate persistent files after installation.

## Dependencies And Integration Points
It is produced by teaish configuration and installed by teaish `Makefile.in`. Tcl's package loader discovers it through `auto_path`. It must match generated DLL names, package names, versions, and init-script tails.

## Risks
Incorrect Tcl major-version detection or DLL substitution will make `package require` fail. The Tcl 8 fallback `load {}` behavior is subtle and depends on load-prefix semantics for statically linked extensions. Optional init script sourcing is conditional on file existence, so missing init files can fail silently when they are expected to provide commands.

## Test Signals
The strongest signal is a clean `package require @TEAISH_PKGNAME@ @TEAISH_VERSION@` under Tcl 8 and Tcl 9 layouts, including installed-tree tests from `make install-test`. Inspecting `auto_path` discovery and load errors helps diagnose bad substitution.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/pkgIndex.tcl.in -->
