## sources/test-tools/xfstests/common/dmthin

Purpose: this shell library builds a dm-thin stack on top of `SCRATCH_DEV` for fstests that need thin provisioning behavior. It derives deterministic mapper names from `$seq`: `thin-data.$seq`, `thin-meta.$seq`, `thin-provision-pool.$seq`, and `thin-vol.$seq`, with corresponding `/dev/mapper/*` paths.

Important APIs: `_dmthin_init` creates linear metadata/data devices, zeros the metadata device, creates a `thin-pool`, sends `create_thin`, and creates the thin volume. `_dmthin_cleanup` tears all mapper devices down after unmounting `SCRATCH_MNT`. `_dmthin_check_fs` temporarily redirects `SCRATCH_DEV` to the thin volume before calling `_check_scratch_fs`. `_dmthin_grow` reloads the data and pool device tables with additional sectors. `_dmthin_set_queue` and `_dmthin_set_fail` choose queue-on-full versus `error_if_no_space` pool behavior. `_dmthin_mount`, `_dmthin_mkfs`, and `_dmthin_try_mkfs` redirect normal scratch mount/mkfs helpers to `DMTHIN_VOL_DEV`.

Control flow: initialization calculates default sizes from `blockdev --getsz`, reserves an offset for metadata, validates the backing device is large enough, cleans previous state, creates mapper targets, and records each table in global variables. Growth queries current tables with `dmsetup table`, computes new sizes, and uses `_dmthin_reload_table` to suspend/load/resume mapper devices.

State and persistence: all device-mapper state is kernel-global and named by `$seq`. The backing scratch device is partitioned logically by table offsets but not partitioned on disk. The helper mutates global `SCRATCH_DEV` only inside `_dmthin_check_fs` and restores it.

Dependencies and integration: it depends on `common/rc` for `_unmount`, `_dmsetup_create`, `_dmsetup_remove`, `_scratch_options`, `_common_dev_mount_options`, `_mount`, `_mkfs_dev`, `_try_mkfs_dev`, `_notrun`, and `_fail`; it also depends on `$DMSETUP_PROG`, `dd`, and `blockdev`. Tests using it must have required the `thin-pool` dm target.

Risks: table parsing uses unanchored `grep` in set-queue/fail paths and field positions from `dmsetup table`, so naming collisions or format changes can misread sizes. `_dmthin_init` contains a likely typo `_notun` on thin-pool creation failure. Cleanup is destructive for devices named with the current `$seq`, so `$seq` uniqueness matters.

Test signals: successful runs should show clean mkfs/mount on `DMTHIN_VOL_DEV`, correct behavior under full-pool mode changes, and clean `_dmthin_check_fs` after unmount. Failures surface as dmsetup errors, stale `/dev/mapper` nodes, or scratch fs check failures.
