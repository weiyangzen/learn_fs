## sources/test-tools/xfstests/tests/btrfs/006

Purpose: this quick volume sanity test exercises basic btrfs informational commands across a multi-device scratch pool.

Control flow: it identifies the first and last scratch pool devices, counts pool devices, formats the whole pool, sets and reads a filesystem label while unmounted, mounts scratch, shows the filesystem by label and UUID, syncs by mountpoint, and displays device stats by mountpoint, scratch device, first pool device, and last pool device.

State and persistence: scratch pool devices are formatted as one btrfs filesystem with label `TestLabel.$seq`. The UUID is discovered from `filesystem show` and used for filtered output.

Dependencies: `common/preamble`, `common/filter.btrfs`, `_require_scratch`, `_require_scratch_dev_pool`, `_scratch_pool_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG`, `_filter_btrfs_filesystem_show`, `_filter_btrfs_device_stats`, and `_filter_spaces`.

Risks: the test assumes pool devices are valid and visible by btrfs-progs both mounted and unmounted. Device stats formatting changes require filter updates. Labels derived from `$seq` must be accepted by btrfs label constraints.

Test signals: stable headings such as `== Set filesystem label`, filtered filesystem-show output with the expected device count, and zeroed/normalized device stats. Failures are direct btrfs command errors or output diffs.
