# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_userhold.c

## Role

Implements snapshot user holds and releases, including temporary holds tied to process exit cleanup.

## Hold Creation

- `dsl_dataset_user_hold_check_one()` validates hold tag length, temporary-hold length restrictions, and duplicate tags on existing snapshots.
- `dsl_dataset_user_hold_check()` validates pool feature support, rejects duplicate snapshot/tag pairs, verifies targets are snapshots, records successful checks in `dduha_chkholds`, and records `ENOENT` entries in the error list without failing the entire operation.
- `dsl_dataset_user_hold_sync_one_impl()` creates `ds_userrefs_obj` when needed, increments `ds_userrefs`, adds the tag timestamp, optionally records pool-wide temporary hold state, and logs history.
- `dsl_dataset_user_hold()` runs the all-or-nothing hold operation as a sync task.

## Temporary Holds

Temporary holds use the pool-wide temporary userref ZAP managed by `dsl_pool_user_hold()` and are also registered with `zfs_onexit_add_cb()`. On process exit, `dsl_dataset_user_release_onexit()` reopens the same loaded pool by name and load GUID, then releases temporary holds by dataset object id.

## Release

- `dsl_dataset_user_release_check_one()` validates snapshot targets, identifies existing hold tags, adds missing hold tags to `errlist`, and marks deferred-destroy snapshots for deletion when the released holds are the last user refs and no long hold exists.
- `dsl_dataset_user_release_check()` validates all requested releases in syncing context.
- `dsl_dataset_user_release_sync_one()` removes temporary pool records if present, removes per-snapshot userref ZAP entries, decrements `ds_userrefs`, and logs history.
- `dsl_dataset_user_release_sync()` also destroys deferred snapshots that become unheld.
- `dsl_dataset_user_release()` handles normal name-keyed releases.
- `dsl_dataset_user_release_tmp()` handles temporary dsobj-keyed releases.

## Snapshot Unmounting

Before release, kernel builds call `zfs_unmount_snap()` because releasing the last hold may destroy deferred snapshots.

## Querying Holds

`dsl_dataset_get_holds()` returns hold tags and timestamps from a snapshot’s `ds_userrefs_obj`.

## Error Semantics

Missing snapshots and missing hold tags are reported in the errlist but do not necessarily fail the entire grouped request. At least one actual release is required for release success, per the documented semantics.
