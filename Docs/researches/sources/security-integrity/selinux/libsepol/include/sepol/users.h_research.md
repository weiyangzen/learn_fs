# sources/security-integrity/selinux/libsepol/include/sepol/users.h

Purpose: Declares public collection operations for SELinux user entries in a policydb.

Important APIs and functions: `sepol_user_modify`, `count`, `exists`, `query`, and `iterate`.

Control flow: Users are keyed by name and represented by `sepol_user_t` records; collection functions search or mutate policydb user symbols and associated role/MLS data.

State and persistence: `modify` updates the in-memory policydb. Query/iterate return record copies.

Dependencies and integration points: Depends on public policydb, user record, handle, and standard size types.

Risks: Modifying users affects context validity, user SID generation, and MLS constraints. Iterator callbacks must not retain freed records.

Test signals: User modification followed by context validation, role/MLS round trips, missing users, and iterator behavior provide coverage.
