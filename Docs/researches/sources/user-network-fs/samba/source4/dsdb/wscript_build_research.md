# sources/user-network-fs/samba/source4/dsdb/wscript_build

## Purpose

`source4/dsdb/wscript_build` defines the Waf build graph for Samba's source4 DSDB libraries, schema subsystem, AD DC services, and Python `samba.dsdb` extension.

## Important APIs, Types, and Functions

The file uses Waf/Samba build declarations: `bld.RECURSE()`, `bld.SAMBA_LIBRARY()`, `bld.SAMBA_SUBSYSTEM()`, `bld.SAMBA_MODULE()`, `bld.SAMBA_PYTHON()`, and `bld.pyembed_libname()`. It declares `samdb`, `samdb-common`, `SAMDB_SCHEMA`, service modules `service_drepl`, `service_kcc`, `service_dns_update`, `service_ft_scanner`, private libraries `dsdb_garbage_collect_tombstones` and `scavenge_dns_records`, and Python module `python_dsdb`.

## Control Flow

At configure/build generation time Waf recurses into `samdb/ldb_modules`, then registers DSDB targets with their source files, autoproto outputs, public/private library status, subsystem placement, service init functions, and dependencies. AD DC service modules are gated by `bld.AD_DC_BUILD_IS_ENABLED()`. Python embedding helper library names are computed before creating `samba/dsdb.so`.

## State and Persistence Behavior

This file does not persist runtime state. It determines build artifacts and generated prototype files such as `samdb/samdb_proto.h`, `common/proto.h`, `schema/proto.h`, and service proto headers. Changes here affect link composition, installed Python extension availability, and which service modules are built into or alongside the Samba service subsystem.

## Dependencies and Integration Points

The build graph connects DSDB code to Kerberos, DRSUAPI NDR, LDB, auth, credentials, schema, KCC/DREPL services, DNS update support, garbage collection, gMSA, Python LDB/RPC/param embedding libraries, and AD DC enablement. The Python DSDB module has an explicit `dcerpc` dependency to avoid unresolved GENSEC symbols after circular dependency pruning.

## Risks and Edge Cases

Dependency omissions can surface only at link time or when loading `samba/dsdb.so`. Service modules are conditional on AD DC support, so tests that assume DREPL/KCC/DNS update services exist must run with AD DC enabled. Build target naming also forms part of Samba's internal module contract; changing init function names or subsystem values can break service registration.

## Test Signals

Useful signals are successful Waf configure/build, generated autoproto headers, linked `samdb` and `samba/dsdb.so`, and AD DC selftests that load DREPL, KCC, DNS update, tombstone garbage collection, and DNS scavenging services.
