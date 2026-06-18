<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/rc -->
# sources/test-tools/blktests/tests/throtl/rc

Purpose: shared `tests/throtl/rc` support for block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. It defines 14 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/null_blk`, `common/scsi_debug`, `common/cgroup`; top-level variables `THROTL_DIR=$(echo $TEST_NAME | tr / _)`, `THROTL_BLKDEV_TYPES=${THROTL_BLKDEV_TYPES:-nullb sdebug}`, `THROTL_NULL_DEV=dev_nullb`; functions `group_requires()` lines 20-27, `_set_throtl_blkdev_type()` lines 29-42, `_configure_throtl_blkdev()` lines 45-88, `_delete_throtl_blkdev()` lines 90-101, `_exit_throtl_blkdev()` lines 103-113, `_set_up_throtl()` lines 116-140, `_clean_up_throtl()` lines 142-153, `_throtl_set_limits()` lines 155-158, `_throtl_remove_limits()` lines 160-163, `_throtl_get_max_io_size()` lines 165-167, `_throtl_set_max_io_size()` lines 169-171, `_throtl_issue_fs_io()` lines 173-190, `_throtl_issue_io()` lines 192-208, `_throtl_test_io()` lines 213-225; external commands `echo`, `grep`, `cat`, `dd`.

Control flow: `group_requires()` uses gates `_have_root`, `_have_null_blk`, `_have_scsi_debug`, `_have_kernel_option BLK_DEV_THROTTLING`, `_have_cgroup2_controller io`, `_have_program bc`.

State and persistence behavior: touches state paths such as `/sys/kernel/config/nullb/$THROTL_DEV/power`, `/sys/block/$THROTL_DEV/device/delete`, `/sys/block/`, `/sys/block/$THROTL_DEV/queue/max_sectors_kb`, `/dev/null`, `/dev/zero`, `$(echo "$TEST_NAME" | tr '/' '_')`, `$((sector_size / 512)`, `$(_cgroup2_base_dir)`, `$(cat /sys/block/"$THROTL_DEV"/dev)`, `$(date +%s.%N)`, `$(echo "$end_time - $start_time" | bc)` uses configfs/sysfs to create or tear down kernel target configuration persists transient cgroup controller limits while IO is running.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `common/rc`, `common/null_blk`, `common/scsi_debug`, `common/cgroup`; requirement gates include `_have_root`, `_have_null_blk`, `_have_scsi_debug`, `_have_kernel_option BLK_DEV_THROTTLING`, `_have_cgroup2_controller io`, `_have_program bc`; runtime command surface includes `echo`, `grep`, `cat`, `dd`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/rc -->
