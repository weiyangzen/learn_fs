# sources/security-integrity/selinux/libsemanage/src/users_local.c

## Purpose
Implements local SELinux user CRUD against the joined local database.

## APIs and control flow
Modify/query/exists/count/iterate/list are dbase wrappers. Delete first calls `lookup_seuser()` to reject removal of a SELinux user still referenced by local login records, then calls `dbase_del()`.

## Dependencies and risks
Depends on joined user local database and local seuser list. `lookup_seuser()` ignores the return from `semanage_seuser_list_local()`, so failures there may leave `records/count` undefined. Deletion safety is important for integrity of login mappings.
