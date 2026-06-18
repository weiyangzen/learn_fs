# sources/security-integrity/selinux/libsemanage/src/seusers_local.c

## Purpose
Implements local CRUD, auditing, and validation for Unix login mappings.

## APIs and control flow
`semanage_seuser_modify_local()` clones incoming data, fills missing MLS range from the target SELinux user when MLS is enabled, queries the previous record with message callbacks muted, writes through `dbase_modify()`, and emits audit records. Delete/query/exists/count/iterate/list are thin local database wrappers. `semanage_seuser_validate_local()` iterates local records and checks referenced SELinux users and MLS containment.

## Dependencies and state
Uses libaudit, sepol MLS checks, policy user APIs, and local/policy databases from the handle. Audit messages include changed sename, role set, and MLS range fields.

## Risks and test signals
Delete audits after `dbase_del()` but then queries the deleted key, which may reduce previous-record detail. Validation comments warn it must run inside a transaction to avoid deadlock/races. MLS fallback depends on a policy user query succeeding.
