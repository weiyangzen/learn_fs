## sources/test-tools/xfstests/tests/btrfs/003

Purpose: this btrfs volume test covers multi-device mkfs profiles, device add, balance, physical device removal/re-addition, replace-like recovery, and device delete.

Important local APIs: `deletable_scratch_dev_pool` checks whether all scratch pool block devices expose a sysfs delete knob. `_test_raid0`, `_test_raid1`, `_test_raid10`, and `_test_single` format the scratch pool with corresponding data/metadata profiles and populate it. `_test_add` starts single-device, adds more devices, and balances. `_test_replace` simulates disk disappearance, verifies a missing device, adds another device, and balances. `_test_remove` deletes the last pool device and verifies `filesystem show` no longer lists it.

Control flow: after requiring scratch, a 4-device scratch pool, and `wipefs`, it skips RAID profiles on zoned btrfs, then runs the single, add, optional replace, and remove paths. Cleanup remounts/re-adds a removed SCSI device if needed.

State and persistence: it repeatedly reformats `SCRATCH_DEV_POOL`, writes populated trees, mutates btrfs device membership, and may remove/re-add a SCSI device via sysfs. Globals `dev_removed` and `removed_dev_htl` coordinate cleanup.

Dependencies: `common/rc` device-pool helpers, `_scratch_pool_mkfs`, `_scratch_mount`, `_populate_fs`, `_run_btrfs_balance_start`, `_devmgt_remove`, `_devmgt_add`, `$BTRFS_UTIL_PROG`, `$WIPEFS_PROG`, and sysfs block device management.

Risks: this is destructive to all devices in `SCRATCH_DEV_POOL`. Sysfs device removal is hardware/environment sensitive and skipped only if delete knobs are absent. The replace test assumes device ordering and can reduce coverage on zoned devices.

Test signals: the test should emit only `Silence is golden` plus full-log diagnostics. Failures include mkfs/add/delete/balance errors, missing-device detection failure, or a deleted device still appearing in `filesystem show`.
