# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deleg.c

## Role

`dsl_deleg.c` implements ZFS delegated administration permissions for DSL directories and datasets. It stores permission grants in ZAP objects, validates allow/unallow operations, retrieves effective delegation data, checks user access, propagates create-time permissions to new datasets, destroys delegation metadata, and checks whether delegation is globally enabled for a pool.

## Permission Storage Model

The file documents a two-level ZAP scheme. The top-level delegation ZAP on a dsl_dir maps “who keys” to jump ZAP objects. Who keys encode:
- local vs descendant permissions,
- users, groups, everyone, create-time grants,
- direct permissions vs named permission sets,
- named set definitions.

Examples include `ul$<id>` for local user permissions, `gd$<id>` for descendant group permissions, `el$` for everyone local permissions, `c-$` for create-time permissions, and `s-$@<name>` for named sets. The second-level jump object contains one boolean-like entry per permission or set name.

## Allow And Unallow Validation

`dsl_deleg_can_allow()` first requires the caller to have `allow`, then requires the caller to already have every permission they are trying to grant. It explicitly rejects delegating `allow` itself.

`dsl_deleg_can_unallow()` requires `allow` and then restricts removal to user/user-set entries matching the caller’s own UID. Non-user entries or entries for a different UID fail with `EPERM`.

These are policy helpers; the actual on-disk mutation is performed later through sync tasks.

## Mutation Sync Tasks

`dsl_deleg_set_sync()` holds the target dsl_dir, creates its `dd_deleg_zapobj` if absent, creates jump objects as needed with `zap_create_link()`, and updates each permission entry in the jump object. Each permission update is logged to pool history.

`dsl_deleg_unset_sync()` removes whole who entries when the nvpair value is not an nvlist, or removes individual permission names from a who jump object. Empty jump objects are destroyed and removed from the top-level ZAP. It logs both whole-who and individual permission removals.

`dsl_deleg_check()` verifies pool support for delegated permissions and that the target dsl_dir can be held. `dsl_deleg_set()` wraps check and set/unset sync functions in `dsl_sync_task()`.

## Retrieval

`dsl_deleg_get()` opens the pool and starting dsl_dir, then walks from the starting dsl_dir upward to the root. For each dsl_dir with a non-empty delegation ZAP, it builds an nvlist of whokeys and their permission nvlists. The resulting nvlist is ordered bottom-up by source dataset name, matching how delegated permissions are inherited and displayed.

## Access Checking

Access checking starts with `dsl_deleg_access()`, which holds the pool and dataset, then calls `dsl_deleg_access_impl()`.

`dsl_deleg_access_impl()`:
- returns `ECANCELED` if delegation is disabled on the pool,
- requires pool version support,
- treats snapshots as descendant-only for permission purposes,
- walks from the dataset dsl_dir to ancestors,
- respects non-global-zone constraints by requiring `zoned=on`,
- loads user/group/everyone named sets for each level,
- recursively expands named sets through set-includes-set entries,
- checks direct user, primary group, everyone, and supplemental groups,
- returns success on the first matching grant.

The named-set expansion uses an AVL tree of `perm_set_t` to avoid duplicate set names and to mark sets that have already been tested.

## Create-Time Permissions And Cleanup

`dsl_deleg_set_create_perms()` walks ancestors of a newly created dsl_dir and copies create-time direct permissions and create-time permission sets to the creator UID on the new dsl_dir. `copy_create_perms()` handles creating the target delegation ZAP/jump objects and copying entries.

`dsl_deleg_destroy()` destroys a delegation ZAP by destroying every jump object and then the top-level delegation object. `dsl_delegation_on()` returns the pool-level delegation setting through `spa_delegation()`.

## Research Notes

The important security boundary is that permission checking is hierarchical and context-sensitive: local grants apply only on the starting dataset, then checks switch to descendant mode while walking ancestors. Snapshots always use descendant mode. Named sets can include other named sets, so the AVL expansion logic is part of the effective authorization model.
