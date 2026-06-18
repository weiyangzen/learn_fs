# sources/user-network-fs/samba/source3/passdb/wscript_build

## Purpose
`wscript_build` declares the source3 passdb build targets for Samba's waf build system. It wires passdb backend modules and the Python passdb extension into the correct subsystems with static/dynamic and feature gating.

## Important APIs, types, and functions
- `bld.SAMBA3_MODULE('pdb_tdbsam', ...)` builds the TDB passdb backend from `pdb_tdb.c`.
- `bld.SAMBA3_MODULE('pdb_ldapsam', ...)` builds LDAP/NDS passdb support from `pdb_ldap.c pdb_nds.c`, gated by module enablement and `HAVE_LDAP`.
- `bld.SAMBA3_MODULE('pdb_smbpasswd', ...)` builds the smbpasswd backend.
- `bld.SAMBA3_MODULE('pdb_samba_dsdb', ...)` builds the AD DC DSDB-backed passdb module only when AD DC build support is enabled.
- `bld.SAMBA3_PYTHON('pypassdb', ...)` builds `py_passdb.c` as `samba/samba3/passdb.so`, depending on `pdb` and public Python embedding/talloc/util dependencies.

## Control flow
The file is evaluated by waf during configuration/build. Each module declaration sets source files, subsystem, dependencies, init function policy, static-module behavior, and enablement conditions. The Python target queries embedded Python library names for `pyrpc_util` and `pytalloc-util`, then declares the extension real name.

## State and persistence behavior
This file does not store runtime state. It controls compiled artifacts and therefore determines which passdb backends and Python bindings are available in the installed Samba tree. Build-time feature flags such as LDAP and AD DC support affect the presence of modules.

## Dependencies and integration points
The declarations tie source3 passdb code to `samba-util`, dbwrap/TDB, LDAP helper libraries, `LIBCLI_AUTH`, `IDMAP`, `samdb`, `pdb`, Python embedding utilities, and pytalloc. `py_passdb.c` depends on this file for being packaged at the Python import path expected by Samba tooling.

## Risks and edge cases
- Feature gating must stay aligned with source dependencies; enabling LDAP or DSDB modules without required libraries would break builds.
- Static module decisions affect runtime backend discovery through passdb initialization and `passdb.get_backends()`.
- Python extension dependency names come from `pyembed_libname`; mismatches can cause link or import failures even when C passdb modules build.

## Test signals
Build tests should cover configurations with and without LDAP and AD DC support, static and shared passdb modules, and importing `samba.samba3.passdb` from the built tree. Runtime `passdb.get_backends()` should reflect enabled modules.
