# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/wscript_build_server

## Purpose
`wscript_build_server` registers the AD DC server-side DSDB LDB modules and audit-related helper tests. It is included only from the AD DC build path.

## Important APIs, Types, and Functions
It defines `DSDB_MODULE_HELPERS_AUDIT`, cmocka audit/group-audit tests, and many `SAMBA_MODULE` targets including `ldb_samba_dsdb`, `ldb_samba_secrets`, `ldb_objectguid`, `ldb_repl_meta_data`, `ldb_schema_load`, `ldb_schema_data`, `ldb_samldb`, `ldb_rootdse`, `ldb_password_hash`, extended-DN modules, partition modules, objectclass modules, linked attributes, operational/managed password, ACL modules, dirsync, notification modules, `ldb_vlv`, `ldb_paged_results`, `ldb_unique_object_sids`, encrypted secrets, audit log modules, and `count_attrs`.

## Control Flow and Behavior
The script declaratively wires each module source to the `ldb` subsystem with an init function and module init name. Tests with error injection use linker wrapping for JSON helper functions. The VLV source in this work item is built as `ldb_vlv` with init function `ldb_vlv_init` and dependency `samdb-common`.

## State and Persistence Behavior
No runtime state is created by the script itself. It controls which shared/internal module artifacts exist in the build tree and which selftests can be run.

## Dependencies and Integration Points
The module dependency graph ties DSDB modules to `samdb`, `samdb-common`, `DSDB_MODULE_HELPERS`, `DSDB_MODULE_HELPERS_AUDIT`, security/NDR libraries, Kerberos, GSSAPI, messaging, GKDI/GMSA, audit logging, and cmocka tests. This file is the central integration point between source files under `ldb_modules` and Samba's AD DC runtime module stack.

## Risks and Edge Cases
Dependency omissions may only appear in partial builds or when optional libraries are disabled. Tests are AD DC/Jansson dependent, so non-AD builds do not exercise audit helpers. Some module names differ from source basenames, so renames require careful update of init functions and module registration names.

## Test Signals
Primary signals are successful AD DC waf builds, module loadability via `ldb_init_module`, and cmocka test execution for audit, group-audit, unique-object-SID, and encrypted-secrets targets.
