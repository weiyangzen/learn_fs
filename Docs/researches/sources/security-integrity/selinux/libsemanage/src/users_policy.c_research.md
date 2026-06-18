# sources/security-integrity/selinux/libsemanage/src/users_policy.c

## Purpose
Provides read-only policy-view operations for joined SELinux user records.

## APIs and integration
`semanage_user_query`, `exists`, `count`, `iterate`, and `list` delegate to the policy user database selected by the handle.

## State and risks
No persistence is changed here. Behavior is only as strong as policy database initialization, record join integrity, and generic dbase validation.
