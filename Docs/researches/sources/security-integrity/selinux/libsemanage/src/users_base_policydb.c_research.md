# sources/security-integrity/selinux/libsemanage/src/users_base_policydb.c

## Purpose
Initializes a policydb-backed database for base SELinux user records.

## APIs and integration
Defines `SEMANAGE_USER_BASE_POLICYDB_RTABLE` with sepol modify/query/count/exists/iterate hooks. `user_base_policydb_dbase_init()` points the policydb layer at active and tmp kernel policy paths. Release delegates to `dbase_policydb_release()`.

## State and risks
Mutations target the tmp kernel policy during transactions and active policy for reads. Add/set are NULL, so behavior is constrained to supported modify/query operations.
