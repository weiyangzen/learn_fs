# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build

## Purpose
`wscript_build` defines the non-server build targets for DSDB LDB module helpers and selected cmocka selftests.

## Important APIs, Types, and Functions
It declares the private grouping library `dsdb-module`, subsystem `DSDB_MODULE_HELPERS` from `util.c`, `acl_util.c`, `schema_util.c`, and `netlogon.c`, subsystem `DSDB_MODULE_HELPER_RIDALLOC` from `ridalloc.c`, and binaries `test_unique_object_sids`, `test_encrypted_secrets_tdb`, and conditionally `test_encrypted_secrets_mdb`.

## Control Flow and Behavior
The build script registers helper subsystems and tests with waf. If AD DC build support is enabled, it processes the separate `server` build rule, which loads `wscript_build_server`.

## State and Persistence Behavior
There is no runtime state. Build artifacts and generated prototypes such as `util_proto.h` and `ridalloc.h` are produced by the Samba build system.

## Dependencies and Integration Points
`DSDB_MODULE_HELPERS` depends on `ldb`, `ndr`, `samdb-common`, and `samba-security`. The RID allocation helper depends on `MESSAGING`. The selftests depend on talloc, samdb, cmocka, gnutls, and backend-specific flags. This file is the entry point that makes `util.c` available to many DSDB modules.

## Risks and Edge Cases
Adding helper source files without updating subsystem dependencies can cause link failures only in selected build configurations. The LMDB encrypted-secrets test is conditional on `HAVE_LMDB`, so test coverage differs across environments. The AD DC gate controls whether server modules are built at all.

## Test Signals
Signals are successful waf configuration/build, generated prototypes, and selftest availability for `test_unique_object_sids` and encrypted-secrets TDB/LMDB variants.
