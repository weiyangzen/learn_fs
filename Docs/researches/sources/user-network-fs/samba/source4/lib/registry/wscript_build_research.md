# sources/user-network-fs/samba/source4/lib/registry/wscript_build

## Purpose

`wscript_build` wires the source4 registry subsystem into Samba's waf build. It generates REGF parsers, builds the private registry library, builds common tooling support, CLI tools, torture tests, and the Python extension module.

## Important APIs, Types, and Functions

Build declarations include `SAMBA_PIDL('PIDL_REG')`, `SAMBA_SUBSYSTEM('TDR_REGF')`, `SAMBA_LIBRARY('registry')`, `SAMBA_SUBSYSTEM('registry_common')`, `SAMBA_BINARY()` entries for `regdiff`, `regpatch`, `regshell`, and `regtree`, `SAMBA_SUBSYSTEM('torture_registry')`, and `SAMBA_PYTHON('py_registry')`.

## Control Flow

At build generation time, PIDL processes `regf.idl` with `--header --tdr-parser`. The registry library compiles interface, utility, Samba-local, patchfile, REGF, hive, local, LDB, and RPC sources. Tool binaries and torture sources depend on that library. Python embedding library names are computed and passed into `py_registry`.

## State and Persistence Behavior

This file affects build artifacts, not runtime registry state. It determines which source files are linked and therefore which backends and tools are available.

## Dependencies and Integration Points

Declared dependencies include `dcerpc`, `samba-util`, `TDR_REGF`, `ldb`, `RPC_NDR_WINREG`, `ldbsamba`, `util_reg`, hostconfig, popt, CMDLINE_S4, SMBREADLINE, torture, pytalloc-util, and pyparam_util. It also declares `registry.h` as a private header.

## Risks and Edge Cases

The active library source list omits `wine.c`, matching that file's placeholder status. Build dependency changes can break Python module linkage or generated REGF parser availability. Because the registry library is private, external consumers should not rely on ABI stability.

## Test Signals

Successful waf build of `registry`, `TDR_REGF`, CLI tools, `torture_registry`, and `samba/registry.so` is the primary signal. Running the torture registry suite verifies the compiled source set coheres.

Source-read signal: reviewed complete local file (69 lines).
