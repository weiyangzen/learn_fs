## sources/test-tools/xfstests/tests/btrfs/023

Purpose: this quick RAID profile test verifies that mkfs creates requested btrfs data and metadata block group profiles.

Important local APIs: `create_group_profile profile` formats the scratch pool with `-d<profile> -m<profile>`. `check_group_profile expected` mounts scratch, captures `btrfs filesystem df`, unmounts, and verifies both `Data` and `Metadata` lines contain the expected profile string.

Control flow: it requires a four-device scratch pool and a non-zoned scratch device, then tests raid0, raid1, and raid10. If `/sys/fs/btrfs/features/raid56` exists, it also tests raid5 and raid6.

State and persistence: each profile test reformats the scratch pool and creates a new btrfs filesystem.

Dependencies: `_require_scratch_dev_pool`, `_require_non_zoned_device`, `_scratch_pool_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG filesystem df`, and sysfs btrfs feature files.

Risks: zoned btrfs supports only single profile, hence the non-zoned gate. RAID56 coverage is conditional on kernel feature exposure. Grep matching assumes `filesystem df` format includes `Data` and `Metadata` profile tokens exactly.

Test signals: expected output is `Silence is golden`; missing profile text for either data or metadata triggers `_fail`.
