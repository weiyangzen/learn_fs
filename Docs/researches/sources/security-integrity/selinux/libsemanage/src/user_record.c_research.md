# sources/security-integrity/selinux/libsemanage/src/user_record.c

## Purpose
Implements public `semanage_user_t` as a joined record composed of base policy data and extra prefix data.

## APIs and control flow
Key functions wrap sepol user keys. Getters/setters delegate name, prefix, MLS, and roles to base/extra records. `semanage_user_create()` allocates base and extra parts and defaults prefix to `user`. `semanage_user_clone()` deep-copies both parts and synchronizes the shared name. `semanage_user_join()` merges optional base/extra halves, creating defaults for missing halves; `semanage_user_split()` clones both halves for persistence.

## State and dependencies
The joined record owns a cached `name` plus owned base and extra records. Database behavior is exposed through `SEMANAGE_USER_RTABLE`.

## Risks and test signals
`semanage_user_join()` error logging dereferences `record1` for a name even when `record1` may be NULL. Name synchronization is multi-step; partial setter failures leave underlying base/extra mutations possible before the cached name is updated.
