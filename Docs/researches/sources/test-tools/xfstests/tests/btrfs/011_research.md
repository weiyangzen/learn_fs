## sources/test-tools/xfstests/tests/btrfs/011

Purpose: this broad replace test exercises btrfs device replace across multiple data/metadata profiles, with optional cancellation, scrub validation, btrfs check, and remount validation.

Important local APIs: `fill_scratch fssize with_cancel` creates inline/data extents and a filler file large enough to keep replace active. `workout mkfs_options num_devs with_cancel fssize` configures a scratch pool plus spare, formats, fills, and invokes replace scenarios. `btrfs_replace_test source target options with_cancel quick` runs replace, optionally cancels it, kills background noise, scrubs, unmounts, checks the filesystem, and remounts with the appropriate source/target device.

Control flow: it requires scratch without final automatic check, five equal-sized scratch devices, at least 10 GiB scratch, and `wipefs`. It filters supported profile configs, then iterates single, dup, raid0, raid1, raid10, mixed, raid5, and raid6 cases where supported. Mirror profiles also test reverse replace with `-r` unless cancellation was involved.

State and persistence: all scratch pool devices are repeatedly wiped and reformatted. `SPARE_DEV`, `SCRATCH_DEV_POOL_SAVED`, and `SCRATCH_DEV_NAME` are managed by rc helpers. Background noise writes `$SCRATCH_MNT/noise`. `$tmp.tmp` stores replace status.

Dependencies: btrfs-progs replace/scrub/filesystem show, `_btrfs_get_profile_configs`, device-pool helpers, `_require_fs_space`, `_check_btrfs_filesystem`, `_scratch_pool_mkfs`, and `$XFS_IO_PROG`.

Risks: destructive multi-device test with timing-sensitive cancellation. If replace finishes before cancel, the test performs a repair replace-back path but still reports a status mismatch. Large direct writes and `/dev/urandom` noise can stress storage heavily.

Test signals: expected stdout is `*** test btrfs replace` and `*** done`. Full-log evidence includes replace status `finished` or `canceled`, scrub success, btrfs check success, and remount success.
