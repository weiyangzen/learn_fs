<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/rc -->
# sources/test-tools/blktests/tests/zbd/rc

Purpose: shared `tests/zbd/rc` support for zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. It defines 15 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/null_blk`, `common/dm`; functions `group_requires()` lines 15-19, `group_device_requires()` lines 21-26, `_fallback_null_blk_zoned()` lines 28-34, `_get_sysfs_variable()` lines 80-101, `_put_sysfs_variable()` lines 103-105, `_get_blkzone_report()` lines 109-188, `_put_blkzone_report()` lines 190-199, `_reset_zones()` lines 203-213, `_find_first_sequential_zone()` lines 215-226, `_find_last_sequential_zone()` lines 228-238, `_find_sequential_zone_in_middle()` lines 241-269, `_find_two_contiguous_seq_zones()` lines 277-294, `_require_test_dev_is_logical()` lines 296-302, `_test_dev_has_dm_map()` lines 304-316, `_get_dev_container_and_sector()` lines 320-375; external commands `blkzone`, `dd`, `echo`, `grep`, `dmsetup`.

Control flow: `group_requires()` uses commands `blkzone`, `dd`; gates `_have_root`, `_have_program blkzone`, `_have_program dd`, `_have_kernel_option BLK_DEV_ZONED`, `_have_null_blk`, `_have_module_param null_blk zoned`. `group_device_requires()` is present and carries the file-specific action body.

State and persistence behavior: touches state paths such as `/dev/nullb1`, `$FULL`, `$(<"${TEST_DEV_PART_SYSFS}"/size)`, `$(<"${_dir}"/size)`, `$(<"${_dir}"/queue/chunk_sectors)`, `$(<"${_dir}"/queue/physical_block_size)`, `$((SYSFS_VARS[SV_PHYS_BLK_SIZE] / 512)`, `$(<"${_dir}"/queue/nr_zones)`, `$(( (SYSFS_VARS[SV_CAPACITY] - 1)`, `$((_tokens[1])`, `$((_tokens[3])`, `$((_tokens[cap_idx])` writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `common/rc`, `common/null_blk`, `common/dm`; requirement gates include `_have_root`, `_have_program blkzone`, `_have_program dd`, `_have_kernel_option BLK_DEV_ZONED`, `_have_null_blk`, `_have_module_param null_blk zoned`, `_require_test_dev_is_logical`; runtime command surface includes `blkzone`, `dd`, `echo`, `grep`, `dmsetup`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/rc -->
