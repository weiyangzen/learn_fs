# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deleg.h

Read status: complete, 91 lines.

Purpose: ZFS delegated administration permission names and DSL delegation APIs.

Key definitions and APIs:
- Permission string constants include create, destroy, snapshot, rollback, clone, promote, rename, mount, share, send, receive, allow, userprop, vscan, quota/used/object-quota variants, hold, release, diff, bookmark, remap, load-key, change-key, and project quota/used variants.
- APIs: `dsl_deleg_get()`, `dsl_deleg_set()`, `dsl_deleg_access()`, `dsl_deleg_access_impl()`, `dsl_deleg_set_create_perms()`, allow/unallow checks, delegation ZAP destroy, and `dsl_delegation_on()`.

Dependencies: DMU, DSL pool, ZFS context, credentials.

Research notes:
- Delegatable property names are also valid delegated permissions.
- This header is the permission vocabulary for administrative checks.
