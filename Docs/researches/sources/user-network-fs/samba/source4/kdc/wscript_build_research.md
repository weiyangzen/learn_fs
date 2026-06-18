# sources/user-network-fs/samba/source4/kdc/wscript_build

## Purpose

This waf build script declares Samba's KDC build graph. It selects Heimdal or MIT service modules, builds KDC/PAC/database subsystems, and registers KDC unit tests.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_MODULE()`, `bld.SAMBA_BINARY()`, `bld.SAMBA_LIBRARY()`, `bld.SAMBA_SUBSYSTEM()`, and `bld.RECURSE()`. Important targets include `service_kdc`, `HDB_SAMBA4`, `KDC-SERVER`, `KPASSWD-SERVICE`, `KDC-GLUE`, `WDC_SAMBA4`, `sdb`, `sdb_hdb`, `sdb_kdb`, `PAC_GLUE`, `db-glue`, `MIT_KDC_IRPC`, `MIT_SAMBA`, `test_db_glue`, and `test_sdb_to_hdb`.

## Control Flow

At build time it chooses bundled or system KDC include paths, gates Heimdal service/tests on `SAMBA4_USES_HEIMDAL`, gates MIT service paths on `SAMBA_USES_MITKDC`, gates KDB conversion on `HAVE_KDB_H`, and recurses into `mit-kdb`.

## State and Persistence Behavior

There is no runtime state. The script persists target metadata and generated autoproto headers such as `sdb_hdb.h` and `sdb_kdb.h`.

## Dependencies and Integration Points

It connects KDC source to host config, credentials, GENSEC, PAC glue, auth policy, LDB/SAMDB, messaging, kpasswd, Heimdal HDB, and MIT KDB libraries. Test binaries are marked for selftest.

## Risks and Edge Cases

The build matrix is sensitive to Heimdal vs MIT and bundled vs system Kerberos. A change may compile only in one matrix, so shared glue requires cross-matrix validation. System header drift can expose portability issues.

## Test Signals

Signals include successful Heimdal and MIT builds, execution of `test_db_glue` and `test_sdb_to_hdb`, fresh autoproto output, and linkage of KDC services and `samba4ktutil`.
