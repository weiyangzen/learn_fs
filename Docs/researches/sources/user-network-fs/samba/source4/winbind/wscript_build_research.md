<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/wscript_build -->
# sources/user-network-fs/samba/source4/winbind/wscript_build

## Purpose

This Waf build fragment declares the Samba4 winbind service wrapper and the ID mapping subsystem.

## Important APIs, Types, and Functions

- `bld.SAMBA_MODULE('service_winbindd', ...)` builds `winbindd.c` as a service module with `server_service_winbindd_init`.
- `bld.SAMBA_SUBSYSTEM('IDMAP', ...)` builds `idmap.c` with generated `idmap_proto.h`.

## Control Flow

Waf processes the service module declaration, then the `IDMAP` subsystem declaration. The service module is not internal, while IDMAP exposes public dependencies on `samdb-common` and `ldbsamba`.

## State and Persistence Behavior

This file affects build artifacts only. Runtime state is created by the compiled service and idmap code.

## Dependencies and Integration Points

`service_winbindd` depends on `process_model` and `UTIL_RUNCMD`; `IDMAP` depends publicly on SAMDB/LDB support. Other build files link against these targets.

## Risks and Edge Cases

Dependency drift in `idmap.c` can require updates here. The service module relies on the runtime presence of the separate `winbindd` daemon binary.

## Test Signals

Build success should generate the service module and `IDMAP` subsystem with prototypes. Runtime service registration validates `service_winbindd`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/wscript_build -->
