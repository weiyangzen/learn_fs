# sources/security-integrity/selinux/libsemanage/src/seusers_policy.c

## Purpose
Provides read-only public policy-view operations for seuser mappings.

## APIs and integration
`semanage_seuser_query`, `exists`, `count`, `iterate`, and `list` all fetch `semanage_seuser_dbase_policy(handle)` and delegate to generic `dbase_*` operations.

## State, risks, and tests
No local persistence is mutated. Correctness depends on the handle selecting a policy database configured by connection setup. Errors and invalid-handle behavior are inherited from the dbase layer.
