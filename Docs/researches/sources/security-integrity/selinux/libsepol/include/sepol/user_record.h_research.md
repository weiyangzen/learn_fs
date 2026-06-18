# sources/security-integrity/selinux/libsepol/include/sepol/user_record.h

Purpose: Declares the public record/key API for SELinux users.

Important APIs and types: Opaque `sepol_user_t` and key type; key create/unpack/extract/free; compare helpers; name getters/setters; MLS level/range getters/setters; role add/delete/has/get/set; create/clone/free.

Control flow: Callers construct a user record with name, authorized roles, and MLS data, then apply/query it through `users.h`.

State and persistence: Records own strings and role arrays in implementation memory; policydb modification persists them in memory until write.

Dependencies and integration points: Depends on handle API; collection operations in `users.h` bridge to policydb user datums.

Risks: Role array ownership, duplicate roles, and MLS enabled/disabled policy constraints require care. Name keys must remain stable.

Test signals: Role add/delete/set/get, MLS fields, clone/free, and policydb query/modify validate it.
