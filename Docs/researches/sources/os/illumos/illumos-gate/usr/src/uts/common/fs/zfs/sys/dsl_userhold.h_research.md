# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_userhold.h

Read status: complete, 57 lines.

Purpose: dataset user hold and release interface.

Key APIs:
- `dsl_dataset_user_hold()` applies named holds from an nvlist, with optional cleanup minor and error nvlist.
- `dsl_dataset_user_release()` releases named holds.
- `dsl_dataset_get_holds()` exports holds for a dataset.
- `dsl_dataset_user_release_tmp()` releases temporary holds for a pool.
- `dsl_dataset_user_hold_check_one()` and `dsl_dataset_user_hold_sync_one()` expose per-hold check/sync helpers.

Dependencies: nvpair/types, DSL pool/dataset and DMU transaction forward declarations.

Research notes:
- User holds prevent snapshot destruction; temporary holds are tied to cleanup minors.
