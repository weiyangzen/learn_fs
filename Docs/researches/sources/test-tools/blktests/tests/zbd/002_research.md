<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/002 -->
# sources/test-tools/blktests/tests/zbd/002

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "report zone".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=report zone`, `CAN_BE_ZONED=1`; functions `fallback_device()` lines 12-14, `cleanup_fallback_device()` lines 16-18, `_check_blkzone_report()` lines 20-109, `test_device()` lines 111-121; external commands `echo`.

Control flow: `test_device()` uses local helpers `_check_blkzone_report`; commands `echo`.

State and persistence behavior: touches state paths such as `$((REPORTED_COUNT - 1)`, `$((ZONE_STARTS[max_idx] + ZONE_LENGTHS[max_idx])`, `$((idx+1)`, `$((cur_start+len)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; runtime command surface includes `echo`.

Risks and test signals: declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/002 -->
